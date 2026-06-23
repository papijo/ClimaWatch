import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.climate_reading import ClimateReading
from app.modules.data_pipeline.http_retry import fetch_with_retry

logger = logging.getLogger(__name__)

NASA_POWER_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
PARAMETERS = "T2M,RH2M,PRECTOTCORR,WS10M,ALLSKY_SFC_UV_INDEX"
FILL_VALUE = -999.0


def _clean(value: float | None) -> float | None:
    if value is None or value == FILL_VALUE:
        return None
    return value


async def fetch(latitude: float, longitude: float) -> dict:
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y%m%d")
    return await fetch_with_retry(
        NASA_POWER_URL,
        params={
            "parameters": PARAMETERS,
            "community": "RE",
            "longitude": longitude,
            "latitude": latitude,
            "start": yesterday,
            "end": yesterday,
            "format": "JSON",
        },
        timeout=60,
    )


def parse(data: dict) -> dict:
    props = data.get("properties", {}).get("parameter", {})
    date_key = next(iter(props.get("T2M", {})), None)
    return {
        "temperature_celsius": _clean(props.get("T2M", {}).get(date_key)),
        "humidity_percent": _clean(props.get("RH2M", {}).get(date_key)),
        "rainfall_mm": _clean(props.get("PRECTOTCORR", {}).get(date_key)),
        "wind_speed_kmh": _clean(props.get("WS10M", {}).get(date_key)),
        "uv_index": _clean(props.get("ALLSKY_SFC_UV_INDEX", {}).get(date_key)),
        "source": "nasa_power",
        "recorded_at": datetime.now(timezone.utc),
    }


async def fetch_and_store(state_id: str, latitude: float, longitude: float, db: Session) -> ClimateReading | None:
    try:
        raw = await fetch(latitude, longitude)
        parsed = parse(raw)
        reading = ClimateReading(state_id=state_id, **parsed)
        db.add(reading)
        return reading
    except Exception:
        logger.exception("NASA POWER fetch failed for state %s", state_id)
        return None
