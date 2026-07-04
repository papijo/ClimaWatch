import asyncio
import base64
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.government_contact import GovernmentContact
from app.models.risk_assessment import RiskAssessment
from app.models.risk_state_change import RiskStateChange
from app.models.state import State
from app.modules.auth.dependencies import require_admin
from app.models.user import User
from app.modules.scheduler.scheduler import get_scheduler_status, run_state_assessment

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _encode_cursor(dt: datetime) -> str:
    return base64.urlsafe_b64encode(dt.isoformat().encode()).decode()


def _decode_cursor(cursor: str) -> datetime:
    return datetime.fromisoformat(base64.urlsafe_b64decode(cursor.encode()).decode())


class ContactRequest(BaseModel):
    state_id: str
    name: str
    title: str
    ministry: str
    email: str
    phone: str | None = None


@router.get("/logs")
def get_risk_change_logs(
    cursor: str | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    q = (
        db.query(RiskStateChange, State.name.label("state_name"))
        .join(State, RiskStateChange.state_id == State.id)
        .order_by(RiskStateChange.changed_at.desc())
    )
    if cursor:
        after_dt = _decode_cursor(cursor)
        q = q.filter(RiskStateChange.changed_at < after_dt)

    rows = q.limit(limit + 1).all()
    has_more = len(rows) > limit
    items = rows[:limit]

    result = [
        {
            "id": change.id,
            "state_id": change.state_id,
            "state_name": state_name,
            "from_level": change.from_level,
            "to_level": change.to_level,
            "reason": change.reason,
            "changed_at": change.changed_at.isoformat(),
        }
        for change, state_name in items
    ]

    next_cursor = _encode_cursor(items[-1][0].changed_at) if has_more and items else None
    return {"items": result, "next_cursor": next_cursor}


@router.get("/assessments")
def get_assessments(
    state_id: str | None = None,
    cursor: str | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    q = db.query(RiskAssessment).order_by(RiskAssessment.assessed_at.desc())
    if state_id:
        q = q.filter(RiskAssessment.state_id == state_id)
    if cursor:
        after_dt = _decode_cursor(cursor)
        q = q.filter(RiskAssessment.assessed_at < after_dt)

    rows = q.limit(limit + 1).all()
    has_more = len(rows) > limit
    items = rows[:limit]

    next_cursor = _encode_cursor(items[-1].assessed_at) if has_more and items else None
    return {"items": items, "next_cursor": next_cursor}


@router.get("/contacts")
def list_contacts(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return db.query(GovernmentContact).order_by(GovernmentContact.created_at.asc()).all()


@router.post("/contacts", status_code=status.HTTP_201_CREATED)
def create_contact(
    body: ContactRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    contact = GovernmentContact(**body.model_dump())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


@router.put("/contacts/{contact_id}")
def update_contact(
    contact_id: str,
    body: ContactRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    contact = db.query(GovernmentContact).filter(GovernmentContact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    for field, value in body.model_dump().items():
        setattr(contact, field, value)
    db.commit()
    db.refresh(contact)
    return contact


@router.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    contact_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    contact = db.query(GovernmentContact).filter(GovernmentContact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(contact)
    db.commit()


@router.post("/trigger/{state_id}", status_code=status.HTTP_202_ACCEPTED)
async def trigger_assessment(
    state_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    state = db.query(State).filter(State.id == state_id).first()
    if not state:
        raise HTTPException(status_code=404, detail="State not found")
    background_tasks.add_task(asyncio.ensure_future, run_state_assessment(state_id))
    return {"message": f"Assessment triggered for {state.name}", "state_id": state_id}


@router.get("/scheduler/status")
def scheduler_status(
    _: User = Depends(require_admin),
):
    return get_scheduler_status()
