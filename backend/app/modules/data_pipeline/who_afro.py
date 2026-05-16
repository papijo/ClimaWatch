"""
WHO AFRO weekly bulletin ingestion.
Expected input: parsed text/JSON from https://www.afro.who.int/health-topics/disease-outbreaks/outbreaks-and-other-emergencies-updates
"""

from datetime import datetime, timezone
from typing import Iterator


def parse_bulletin(records: list[dict]) -> Iterator[dict]:
    for record in records:
        try:
            yield {
                "disease_name": record["disease"].strip(),
                "alert_level": _map_level(record.get("grade", "watch")),
                "source": "who_afro",
                "description": record.get("summary", "").strip(),
                "affected_lgas": None,
                "state_name": record.get("state"),
                "reported_at": _parse_date(record.get("date")),
                "is_active": True,
            }
        except (KeyError, TypeError):
            continue


def _map_level(raw: str) -> str:
    raw = raw.lower()
    if "grade 3" in raw or "emergency" in raw:
        return "emergency"
    if "grade 2" in raw or "warning" in raw:
        return "warning"
    return "watch"


def _parse_date(val: str | None) -> datetime:
    if val:
        try:
            return datetime.fromisoformat(val).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return datetime.now(timezone.utc)
