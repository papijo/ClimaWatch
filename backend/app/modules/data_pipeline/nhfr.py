"""
NHFR (National Health Facility Registry) ingestion via HDX dataset download.
Expects a CSV exported from https://data.humdata.org/dataset/nigeria-health-facilities
"""

import csv
import io
import logging
from typing import Iterator

from sqlalchemy.orm import Session

from app.models.health_facility import HealthFacility
from app.models.state import State

logger = logging.getLogger(__name__)


def parse_csv(raw_csv: str) -> Iterator[dict]:
    reader = csv.DictReader(io.StringIO(raw_csv))
    for row in reader:
        try:
            yield {
                "name": row.get("facility_name", "").strip(),
                "lga": row.get("lga", "").strip(),
                "state_name": row.get("state", "").strip(),
                "facility_type": _map_type(row.get("facility_type", "")),
                "ownership": _map_ownership(row.get("ownership", "")),
                "latitude": _float_or_none(row.get("latitude")),
                "longitude": _float_or_none(row.get("longitude")),
                "bed_count": _int_or_none(row.get("beds")),
                "source": "nhfr",
            }
        except Exception:
            continue


def ingest(raw_csv: str, db: Session) -> dict[str, int]:
    state_cache: dict[str, str | None] = {}
    created = 0
    skipped = 0
    unresolved = 0

    for record in parse_csv(raw_csv):
        state_name = record.pop("state_name")

        if state_name not in state_cache:
            state = db.query(State).filter(State.name.ilike(f"%{state_name}%")).first()
            state_cache[state_name] = state.id if state else None

        state_id = state_cache[state_name]
        if not state_id:
            unresolved += 1
            continue

        existing = (
            db.query(HealthFacility)
            .filter(
                HealthFacility.state_id == state_id,
                HealthFacility.name == record["name"],
                HealthFacility.lga == record["lga"],
            )
            .first()
        )
        if existing:
            skipped += 1
            continue

        facility = HealthFacility(state_id=state_id, **record)
        db.add(facility)
        created += 1

    db.commit()
    result = {"created": created, "skipped": skipped, "unresolved_state": unresolved}
    logger.info("NHFR ingest complete: %s", result)
    return result


def _map_type(raw: str) -> str:
    raw = raw.lower()
    if "tertiary" in raw or "teaching" in raw or "federal" in raw:
        return "tertiary"
    if "secondary" in raw or "general" in raw or "specialist" in raw:
        return "secondary"
    return "primary"


def _map_ownership(raw: str) -> str:
    raw = raw.lower()
    if "private" in raw:
        return "private"
    if "ngo" in raw or "mission" in raw or "international" in raw:
        return "ngo"
    if "church" in raw or "mosque" in raw or "faith" in raw:
        return "faith_based"
    return "public"


def _float_or_none(val: str | None) -> float | None:
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _int_or_none(val: str | None) -> int | None:
    try:
        return int(val)
    except (TypeError, ValueError):
        return None
