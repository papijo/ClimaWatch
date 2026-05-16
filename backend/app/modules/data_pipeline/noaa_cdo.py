import httpx
from datetime import datetime, timedelta, timezone

from app.config import settings

NOAA_CDO_URL = "https://www.ncdc.noaa.gov/cdo-web/api/v2/data"


async def fetch(station_id: str) -> dict:
    today = datetime.now(timezone.utc)
    start = (today - timedelta(days=7)).strftime("%Y-%m-%d")
    end = today.strftime("%Y-%m-%d")
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            NOAA_CDO_URL,
            headers={"token": settings.NOAA_TOKEN},
            params={
                "datasetid": "GHCND",
                "stationid": station_id,
                "startdate": start,
                "enddate": end,
                "datatypeid": "TMAX,TMIN,PRCP",
                "limit": 7,
                "units": "metric",
            },
        )
        response.raise_for_status()
        return response.json()


def parse(data: dict) -> dict | None:
    results = data.get("results", [])
    if not results:
        return None
    latest = results[-1]
    return {
        "temperature_celsius": latest.get("value"),
        "source": "noaa_cdo",
        "recorded_at": datetime.now(timezone.utc),
    }
