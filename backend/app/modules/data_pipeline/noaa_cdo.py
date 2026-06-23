import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from app.models.climate_reading import ClimateReading
from app.modules.data_pipeline.http_retry import fetch_with_retry

logger = logging.getLogger(__name__)

NOAA_CDO_URL = "https://www.ncdc.noaa.gov/cdo-web/api/v2/data"
STATIONS_FILE = Path(__file__).resolve().parents[3] / "data" / "state_noaa_stations.json"

_rate_lock = asyncio.Lock()
_last_request_time: float = 0


def load_station_mapping() -> dict[str, str | None]:
    with open(STATIONS_FILE) as f:
        data = json.load(f)
    data.pop("_comment", None)
    return data


def get_station_id(state_code: str) -> str | None:
    mapping = load_station_mapping()
    return mapping.get(state_code)


async def _rate_limited_fetch(url: str, **kwargs) -> dict:
    global _last_request_time
    async with _rate_lock:
        now = asyncio.get_event_loop().time()
        elapsed = now - _last_request_time
        if elapsed < 1.0:
            await asyncio.sleep(1.0 - elapsed)
        _last_request_time = asyncio.get_event_loop().time()
    return await fetch_with_retry(url, **kwargs)


async def fetch(station_id: str) -> dict:
    today = datetime.now(timezone.utc)
    start = (today - timedelta(days=7)).strftime("%Y-%m-%d")
    end = today.strftime("%Y-%m-%d")
    return await _rate_limited_fetch(
        NOAA_CDO_URL,
        headers={"token": settings.NOAA_TOKEN},
        params={
            "datasetid": "GHCND",
            "stationid": station_id,
            "startdate": start,
            "enddate": end,
            "datatypeid": "TMAX,TMIN,PRCP",
            "limit": 21,
            "units": "metric",
        },
        timeout=30,
    )


def parse(data: dict) -> dict | None:
    results = data.get("results", [])
    if not results:
        return None

    tmax_values = [r["value"] for r in results if r.get("datatype") == "TMAX"]
    tmin_values = [r["value"] for r in results if r.get("datatype") == "TMIN"]
    prcp_values = [r["value"] for r in results if r.get("datatype") == "PRCP"]

    temp = None
    if tmax_values and tmin_values:
        temp = (tmax_values[-1] / 10 + tmin_values[-1] / 10) / 2
    elif tmax_values:
        temp = tmax_values[-1] / 10

    rainfall = prcp_values[-1] / 10 if prcp_values else None

    return {
        "temperature_celsius": temp,
        "rainfall_mm": rainfall,
        "source": "noaa_cdo",
        "recorded_at": datetime.now(timezone.utc),
    }


async def fetch_and_store(state_id: str, state_code: str, db: Session) -> ClimateReading | None:
    station_id = get_station_id(state_code)
    if not station_id:
        logger.info("No NOAA station mapped for state %s", state_code)
        return None
    try:
        raw = await fetch(station_id)
        parsed = parse(raw)
        if parsed is None:
            logger.info("No NOAA data returned for station %s (state %s)", station_id, state_code)
            return None
        reading = ClimateReading(state_id=state_id, **parsed)
        db.add(reading)
        return reading
    except Exception:
        logger.exception("NOAA CDO fetch failed for state %s (station %s)", state_code, station_id)
        return None
