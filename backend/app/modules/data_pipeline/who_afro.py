"""
WHO AFRO weekly bulletin ingestion.
Expected input: parsed text/JSON from https://www.afro.who.int/health-topics/disease-outbreaks/outbreaks-and-other-emergencies-updates
"""

import logging
from datetime import datetime, timezone
from typing import Iterator

from sqlalchemy.orm import Session

from app.models.disease_alert import DiseaseAlert
from app.models.state import State
from app.modules.alert_engine.website_alerts import create_disease_website_alert

logger = logging.getLogger(__name__)


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


def ingest(records: list[dict], db: Session) -> dict[str, int]:
    state_cache: dict[str, str | None] = {}
    created = 0
    skipped = 0

    for parsed in parse_bulletin(records):
        state_name = parsed.pop("state_name")
        state_id = _resolve_state(state_name, state_cache, db)

        existing = (
            db.query(DiseaseAlert)
            .filter(
                DiseaseAlert.disease_name == parsed["disease_name"],
                DiseaseAlert.source == "who_afro",
                DiseaseAlert.state_id == state_id,
                DiseaseAlert.is_active.is_(True),
            )
            .first()
        )
        if existing:
            skipped += 1
            continue

        alert = DiseaseAlert(state_id=state_id, **parsed)
        db.add(alert)
        db.flush()
        create_disease_website_alert(db, alert)
        created += 1

    db.commit()
    result = {"created": created, "skipped": skipped}
    logger.info("WHO AFRO ingest complete: %s", result)
    return result


def _resolve_state(name: str | None, cache: dict, db: Session) -> str | None:
    if not name:
        return None
    if name not in cache:
        state = db.query(State).filter(State.name.ilike(f"%{name}%")).first()
        cache[name] = state.id if state else None
    return cache[name]


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
