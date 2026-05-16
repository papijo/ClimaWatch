from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.active_alert import ActiveAlert
from app.models.state import State


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
