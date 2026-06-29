import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.active_alert import ActiveAlert
from app.models.disease_alert import DiseaseAlert
from app.models.state import State

logger = logging.getLogger(__name__)

DISEASE_LEVEL_TO_RISK = {
    "warning": "HIGH",
    "emergency": "CRITICAL",
}


def create_alert(db: Session, state: State, title: str, description: str, risk_level: str) -> ActiveAlert:
    alert = ActiveAlert(
        state_id=state.id,
        title=title,
        description=description,
        risk_level=risk_level,
        is_active=True,
        started_at=datetime.now(timezone.utc),
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def resolve_alerts(db: Session, state_id: str) -> int:
    now = datetime.now(timezone.utc)
    updated = (
        db.query(ActiveAlert)
        .filter(ActiveAlert.state_id == state_id, ActiveAlert.is_active.is_(True))
        .all()
    )
    for alert in updated:
        alert.is_active = False
        alert.ended_at = now
    db.commit()
    return len(updated)


def get_active_alerts(db: Session) -> list[ActiveAlert]:
    return (
        db.query(ActiveAlert)
        .filter(ActiveAlert.is_active.is_(True))
        .order_by(ActiveAlert.started_at.desc())
        .all()
    )


def create_disease_website_alert(db: Session, disease_alert: DiseaseAlert) -> ActiveAlert | None:
    """Create a website ActiveAlert from a DiseaseAlert if the level warrants it."""
    risk_level = DISEASE_LEVEL_TO_RISK.get(disease_alert.alert_level)
    if not risk_level or not disease_alert.state_id:
        return None

    state = db.query(State).filter(State.id == disease_alert.state_id).first()
    if not state:
        return None

    title = f"Disease Alert: {disease_alert.disease_name} — {state.name}"
    description = disease_alert.description

    alert = create_alert(db, state, title, description, risk_level)
    logger.info(
        "Website alert created from disease alert: %s (%s) for %s",
        disease_alert.disease_name, risk_level, state.name,
    )
    return alert
