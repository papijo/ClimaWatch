import httpx
from datetime import datetime, timedelta, timezone

NASA_POWER_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"

PARAMETERS = "T2M,RH2M,PRECTOTCORR,WS10M,ALLSKY_SFC_UVA"


async def fetch(latitude: float, longitude: float) -> dict:
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y%m%d")
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.get(
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
        )
        response.raise_for_status()
        return response.json()


def parse(data: dict) -> dict:
    props = data.get("properties", {}).get("parameter", {})
    date_key = next(iter(props.get("T2M", {})), None)
    return {
        "temperature_celsius": props.get("T2M", {}).get(date_key),
        "humidity_percent": props.get("RH2M", {}).get(date_key),
        "rainfall_mm": props.get("PRECTOTCORR", {}).get(date_key),
        "wind_speed_kmh": props.get("WS10M", {}).get(date_key),
        "uv_index": None,
        "air_quality_index": None,
        "source": "nasa_power",
        "recorded_at": datetime.now(timezone.utc),
    }
