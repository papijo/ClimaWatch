from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.risk_state_change import RiskStateChange
from app.models.state import State


def apply_risk_transition(db: Session, state: State, new_level: str, reason: str | None = None) -> bool:
    """Returns True if the risk level actually changed."""
    if state.current_risk_level == new_level:
        return False

    change = RiskStateChange(
        state_id=state.id,
        from_level=state.current_risk_level,
        to_level=new_level,
        reason=reason,
        changed_at=datetime.now(timezone.utc),
    )
    db.add(change)
    state.current_risk_level = new_level
    db.commit()
    return True


def get_consecutive_low_count(db: Session, state_id: str) -> int:
    """Count consecutive LOW assessments from the most recent risk_state_changes."""
    from app.models.risk_assessment import RiskAssessment
    recent = (
        db.query(RiskAssessment)
        .filter(RiskAssessment.state_id == state_id)
        .order_by(RiskAssessment.assessed_at.desc())
        .limit(2)
        .all()
    )
    return sum(1 for r in recent if r.risk_level == "LOW")
