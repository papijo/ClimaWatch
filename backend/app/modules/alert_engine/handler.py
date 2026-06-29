"""Alert engine handler — ties together website alerts, subscriber lookup, and email dispatch.

Registered as a callback on the risk manager so it fires automatically on every
risk level transition.
"""

import logging

from sqlalchemy.orm import Session

from app.models.risk_assessment import RiskAssessment
from app.models.state import State
from app.modules.alert_engine.email_dispatch import dispatch_alerts
from app.modules.alert_engine.subscribers import get_subscribers
from app.modules.alert_engine.website_alerts import create_alert, resolve_alerts

logger = logging.getLogger(__name__)


def on_risk_transition(
    db: Session,
    state: State,
    old_level: str,
    new_level: str,
) -> None:
    """Risk manager callback — fires on every risk level change."""
    if new_level in ("HIGH", "CRITICAL"):
        _handle_escalation(db, state, new_level)
    elif old_level in ("HIGH", "CRITICAL") and new_level in ("LOW", "MODERATE"):
        _handle_de_escalation(db, state)


def _handle_escalation(db: Session, state: State, new_level: str) -> None:
    latest = (
        db.query(RiskAssessment)
        .filter(RiskAssessment.state_id == state.id)
        .order_by(RiskAssessment.assessed_at.desc())
        .first()
    )
    advisory = latest.advisory_en if latest else "No advisory available."

    title = f"{new_level} Climate-Health Alert — {state.name}"
    description = advisory

    create_alert(db, state, title, description, new_level)
    logger.info("Website alert created for %s at %s", state.name, new_level)

    subscribers = get_subscribers(db, state.id, new_level)
    if subscribers:
        result = dispatch_alerts(subscribers, state.name, new_level, advisory)
        logger.info("Email dispatch for %s: %s", state.name, result)


def _handle_de_escalation(db: Session, state: State) -> None:
    resolved = resolve_alerts(db, state.id)
    if resolved:
        logger.info("Resolved %d active alerts for %s", resolved, state.name)
