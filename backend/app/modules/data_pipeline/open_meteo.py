import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.climate_reading import ClimateReading
from app.modules.data_pipeline.http_retry import fetch_with_retry

logger = logging.getLogger(__name__)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

PARAMS = {
    "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,uv_index",
    "forecast_days": 1,
}


async def fetch(latitude: float, longitude: float) -> dict:
    return await fetch_with_retry(
        OPEN_METEO_URL,
        params={"latitude": latitude, "longitude": longitude, **PARAMS},
        timeout=30,
    )


def parse(data: dict) -> dict:
    current = data.get("current", {})
    return {
        "temperature_celsius": current.get("temperature_2m"),
        "humidity_percent": current.get("relative_humidity_2m"),
        "rainfall_mm": current.get("precipitation"),
        "wind_speed_kmh": current.get("wind_speed_10m"),
        "uv_index": current.get("uv_index"),
        "source": "open_meteo",
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
        logger.exception("Open-Meteo fetch failed for state %s", state_id)
        return None
