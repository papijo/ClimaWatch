import httpx
from datetime import datetime, timezone


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

PARAMS = {
    "hourly": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,uv_index",
    "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,uv_index",
    "forecast_days": 1,
}


async def fetch(latitude: float, longitude: float) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            OPEN_METEO_URL,
            params={"latitude": latitude, "longitude": longitude, **PARAMS},
        )
        response.raise_for_status()
        return response.json()


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
