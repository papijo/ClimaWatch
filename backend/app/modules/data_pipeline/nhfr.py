"""
NHFR (National Health Facility Registry) ingestion.
Supports the GRID3 Nigeria health facilities CSV (v2.0) from:
  https://data.humdata.org/dataset/nigeria-health-facilities

Run from backend/:
  python scripts/ingest_nhfr.py ../GRID3_NGA_health_facilities_v2_0_3768559736750290399.csv
"""

import csv
import io
import logging
from typing import Iterator

from sqlalchemy.orm import Session

from app.models.health_facility import HealthFacility
from app.models.state import State

logger = logging.getLogger(__name__)

BATCH_SIZE = 500

STATE_NAME_ALIASES: dict[str, str] = {
    "fct": "FCT Abuja",
}


def parse_csv(raw_csv: str) -> Iterator[dict]:
    reader = csv.DictReader(io.StringIO(raw_csv))
    for row in reader:
        try:
            yield {
                "name": row.get("facility_name", "").strip(),
                "lga": row.get("lga", "").strip(),
                "state_name": row.get("state", "").strip(),
                "facility_type": _map_type(row.get("facility_level", "")),
                "ownership": _map_ownership(row.get("ownership", "")),
                "category": _clean_category(row.get("facility_level_option", "")),
                "latitude": _float_or_none(row.get("latitude")),
                "longitude": _float_or_none(row.get("longitude")),
                "source": "nhfr",
            }
        except Exception:
            continue


def ingest(raw_csv: str, db: Session) -> dict[str, int]:
    state_cache: dict[str, str | None] = _build_state_cache(db)
    created = 0
    skipped = 0
    unresolved = 0
    pending = 0

    for record in parse_csv(raw_csv):
        state_name = record.pop("state_name")
        state_id = state_cache.get(state_name.lower())

        if not state_id:
            unresolved += 1
            continue

        existing = (
            db.query(HealthFacility.id)
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
        pending += 1

        if pending >= BATCH_SIZE:
            db.flush()
            pending = 0

    db.commit()
    result = {"created": created, "skipped": skipped, "unresolved_state": unresolved}
    logger.info("NHFR ingest complete: %s", result)
    return result


def _build_state_cache(db: Session) -> dict[str, str]:
    """Pre-load all states into a lowercase-name → id lookup, including aliases."""
    cache: dict[str, str] = {}
    for state in db.query(State).all():
        cache[state.name.lower()] = state.id
    for alias, canonical in STATE_NAME_ALIASES.items():
        canonical_id = cache.get(canonical.lower())
        if canonical_id:
            cache[alias] = canonical_id
    return cache


def _map_type(raw: str) -> str:
    val = raw.strip().lower()
    if val == "tertiary":
        return "tertiary"
    if val == "secondary":
        return "secondary"
    if val == "primary":
        return "primary"
    return "unknown"


def _map_ownership(raw: str) -> str:
    val = raw.strip().lower()
    if val == "public":
        return "public"
    if val == "private":
        return "private"
    if "ngo" in val or "mission" in val:
        return "ngo"
    if "faith" in val or "church" in val or "mosque" in val:
        return "faith_based"
    return "unknown"


def _clean_category(raw: str) -> str | None:
    val = raw.strip()
    if not val or val.lower() == "unknown":
        return None
    return val


def _float_or_none(val: str | None) -> float | None:
    try:
        return float(val)
    except (TypeError, ValueError):
        return None
