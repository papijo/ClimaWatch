import logging

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.user_subscription import UserSubscription

logger = logging.getLogger(__name__)

LEVEL_TO_FIELD = {
    "MODERATE": "notify_moderate",
    "HIGH": "notify_high",
    "CRITICAL": "notify_critical",
}


def get_subscribers(db: Session, state_id: str, risk_level: str) -> list[dict]:
    """Return subscribers who should be notified for the given state and risk level.

    Returns a list of dicts with keys: email, full_name, user_id.
    """
    field_name = LEVEL_TO_FIELD.get(risk_level)
    if not field_name:
        return []

    notify_field = getattr(UserSubscription, field_name)

    rows = (
        db.query(User.email, User.full_name, User.id)
        .join(UserSubscription, UserSubscription.user_id == User.id)
        .filter(
            UserSubscription.state_id == state_id,
            UserSubscription.is_active.is_(True),
            User.is_active.is_(True),
            notify_field.is_(True),
        )
        .all()
    )

    subscribers = [
        {"email": email, "full_name": full_name, "user_id": uid}
        for email, full_name, uid in rows
    ]

    logger.info(
        "Found %d subscribers for state %s at %s level",
        len(subscribers), state_id, risk_level,
    )
    return subscribers
