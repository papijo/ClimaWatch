"""
NCDC (Nigeria Centre for Disease Control) disease alert ingestion.
Parses structured data from https://ncdc.gov.ng/diseases/sitreps
Expected input: a list of dicts from a scraped/downloaded weekly situation report.
"""

from datetime import datetime, timezone
from typing import Iterator


def parse_sitrep(records: list[dict]) -> Iterator[dict]:
    for record in records:
        try:
            yield {
                "disease_name": record["disease"].strip(),
                "alert_level": _map_level(record.get("severity", "watch")),
                "source": "ncdc",
                "description": record.get("summary", "").strip(),
                "affected_lgas": record.get("lgas"),
                "state_name": record.get("state"),
                "reported_at": _parse_date(record.get("date")),
                "is_active": True,
            }
        except (KeyError, TypeError):
            continue


def _map_level(raw: str) -> str:
    raw = raw.lower()
    if "emergency" in raw or "outbreak" in raw:
        return "emergency"
    if "warning" in raw or "alert" in raw:
        return "warning"
    return "watch"


def _parse_date(val: str | None) -> datetime:
    if val:
        try:
            return datetime.fromisoformat(val).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return datetime.now(timezone.utc)
