import logging
from datetime import datetime, timezone
from typing import Callable

from sqlalchemy.orm import Session

from app.models.risk_assessment import RiskAssessment
from app.models.risk_state_change import RiskStateChange
from app.models.state import State

logger = logging.getLogger(__name__)

TransitionCallback = Callable[[Session, State, str, str], None]

_on_transition_callbacks: list[TransitionCallback] = []


def register_transition_callback(callback: TransitionCallback) -> None:
    _on_transition_callbacks.append(callback)


def apply_risk_transition(
    db: Session,
    state: State,
    new_level: str,
    reason: str | None = None,
) -> bool:
    """Apply a risk level transition for a state.

    Returns True if the level actually changed.
    """
    old_level = state.current_risk_level
    if old_level == new_level:
        return False

    change = RiskStateChange(
        state_id=state.id,
        from_level=old_level,
        to_level=new_level,
        reason=reason,
        changed_at=datetime.now(timezone.utc),
    )
    db.add(change)
    state.current_risk_level = new_level
    db.commit()

    logger.info(
        "Risk transition for %s: %s -> %s (reason: %s)",
        state.name, old_level, new_level, reason,
    )

    for callback in _on_transition_callbacks:
        try:
            callback(db, state, old_level, new_level)
        except Exception:
            logger.exception("Transition callback failed for %s", state.name)

    return True


def get_consecutive_low_count(db: Session, state_id: str) -> int:
    """Count consecutive LOW assessments from the most recent backwards."""
    recent = (
        db.query(RiskAssessment.risk_level)
        .filter(RiskAssessment.state_id == state_id)
        .order_by(RiskAssessment.assessed_at.desc())
        .limit(10)
        .all()
    )
    count = 0
    for (level,) in recent:
        if level == "LOW":
            count += 1
        else:
            break
    return count


def should_downgrade_schedule(db: Session, state_id: str) -> bool:
    """Return True if the state has had 2+ consecutive LOW assessments,
    meaning it should return to the default 12-hour cycle."""
    return get_consecutive_low_count(db, state_id) >= 2


def build_transition_reason(assessment: RiskAssessment) -> str:
    """Build a human-readable reason string from an assessment."""
    return (
        f"AI assessment scored {assessment.overall_score:.1f}/100 "
        f"(climate={assessment.climate_score:.1f}, "
        f"health={assessment.health_score:.1f}, "
        f"vulnerability={assessment.vulnerability_score:.1f})"
    )
