import asyncio
import logging
from math import ceil

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import SessionLocal, get_db
from app.models.climate_reading import ClimateReading
from app.models.government_contact import GovernmentContact
from app.models.risk_assessment import RiskAssessment
from app.models.risk_state_change import RiskStateChange
from app.models.state import State
from app.models.user import User
from app.modules.auth.dependencies import require_admin
from app.modules.data_pipeline import nasa_power, noaa_cdo, open_meteo
from app.modules.scheduler.scheduler import get_scheduler_status, run_state_assessment

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ── Request schemas ────────────────────────────────────────────────────────────

class ContactRequest(BaseModel):
    state_id: str
    name: str
    title: str
    ministry: str
    email: str
    phone: str | None = None


def _paginate(q, page: int, limit: int) -> tuple:
    """Return (items, total, total_pages) for a SQLAlchemy query."""
    total = q.count()
    total_pages = max(1, ceil(total / limit))
    items = q.offset((page - 1) * limit).limit(limit).all()
    return items, total, total_pages


# ── Risk change logs ───────────────────────────────────────────────────────────

@router.get("/logs")
def get_risk_change_logs(
    search: str | None = None,
    sort_dir: str = "desc",
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    q = (
        db.query(RiskStateChange, State.name.label("state_name"))
        .join(State, RiskStateChange.state_id == State.id)
    )

    if search:
        q = q.filter(State.name.ilike(f"%{search}%"))

    q = q.order_by(
        RiskStateChange.changed_at.asc() if sort_dir == "asc"
        else RiskStateChange.changed_at.desc()
    )

    rows, total, total_pages = _paginate(q, page, limit)

    return {
        "items": [
            {
                "id": change.id,
                "state_id": change.state_id,
                "state_name": state_name,
                "from_level": change.from_level,
                "to_level": change.to_level,
                "reason": change.reason,
                "changed_at": change.changed_at.isoformat(),
            }
            for change, state_name in rows
        ],
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
    }


# ── Assessments ────────────────────────────────────────────────────────────────

@router.get("/assessments")
def get_assessments(
    state_id: str | None = None,
    search: str | None = None,
    sort_dir: str = "desc",
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    q = (
        db.query(RiskAssessment, State.name.label("state_name"))
        .join(State, RiskAssessment.state_id == State.id)
    )

    if state_id:
        q = q.filter(RiskAssessment.state_id == state_id)

    if search:
        q = q.filter(State.name.ilike(f"%{search}%"))

    q = q.order_by(
        RiskAssessment.assessed_at.asc() if sort_dir == "asc"
        else RiskAssessment.assessed_at.desc()
    )

    rows, total, total_pages = _paginate(q, page, limit)

    return {
        "items": [
            {
                "id": a.id,
                "state_id": a.state_id,
                "state_name": sname,
                "risk_level": a.risk_level,
                "overall_score": a.overall_score,
                "climate_score": a.climate_score,
                "health_score": a.health_score,
                "vulnerability_score": a.vulnerability_score,
                "advisory_en": a.advisory_en,
                "advisory_ha": a.advisory_ha,
                "advisory_yo": a.advisory_yo,
                "advisory_ig": a.advisory_ig,
                "assessed_at": a.assessed_at.isoformat(),
            }
            for a, sname in rows
        ],
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
    }


# ── Government contacts ────────────────────────────────────────────────────────

@router.get("/contacts")
def list_contacts(
    search: str | None = None,
    sort_by: str = "state",
    sort_dir: str = "asc",
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    q = (
        db.query(GovernmentContact, State.name.label("state_name"))
        .join(State, GovernmentContact.state_id == State.id)
    )

    if search:
        term = f"%{search}%"
        q = q.filter(
            or_(
                GovernmentContact.name.ilike(term),
                GovernmentContact.email.ilike(term),
                GovernmentContact.ministry.ilike(term),
                State.name.ilike(term),
            )
        )

    sort_col = {
        "state": State.name,
        "name": GovernmentContact.name,
        "ministry": GovernmentContact.ministry,
        "created_at": GovernmentContact.created_at,
    }.get(sort_by, State.name)

    q = q.order_by(
        sort_col.desc() if sort_dir == "desc" else sort_col.asc(),
        GovernmentContact.created_at.asc(),
    )

    rows, total, total_pages = _paginate(q, page, limit)

    return {
        "items": [
            {
                "id": c.id,
                "state_id": c.state_id,
                "state_name": sname,
                "name": c.name,
                "title": c.title,
                "ministry": c.ministry,
                "phone": c.phone,
                "email": c.email,
            }
            for c, sname in rows
        ],
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
    }


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


# ── Assessment trigger ─────────────────────────────────────────────────────────

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


# ── Scheduler status ───────────────────────────────────────────────────────────

@router.get("/scheduler/status")
def scheduler_status(
    _: User = Depends(require_admin),
):
    return get_scheduler_status()


# ── Data pipeline ──────────────────────────────────────────────────────────────

_PIPELINE_META = {
    "open_meteo": {
        "label": "Open-Meteo",
        "type": "api",
        "description": "Live weather & climate data — hourly readings for all 37 states",
        "source_enum": "open_meteo",
        "can_trigger": True,
    },
    "nasa_power": {
        "label": "NASA POWER",
        "type": "api",
        "description": "Solar radiation & meteorological data — NASA satellite observations",
        "source_enum": "nasa_power",
        "can_trigger": True,
    },
    "noaa_cdo": {
        "label": "NOAA CDO",
        "type": "api",
        "description": "Historical climate records — NOAA Climate Data Online (requires NOAA_TOKEN)",
        "source_enum": "noaa_cdo",
        "can_trigger": True,
    },
    "nhfr": {
        "label": "NHFR (HDX)",
        "type": "dataset",
        "description": "National Health Facility Registry — ingested via CSV upload script",
        "source_enum": None,
        "can_trigger": False,
    },
    "ncdc": {
        "label": "NCDC",
        "type": "dataset",
        "description": "NCDC disease surveillance data — ingested via manual extraction",
        "source_enum": None,
        "can_trigger": False,
    },
    "who_afro": {
        "label": "WHO AFRO",
        "type": "dataset",
        "description": "WHO Africa Regional Office bulletin — ingested via manual processing",
        "source_enum": None,
        "can_trigger": False,
    },
}


@router.get("/pipeline/status")
def pipeline_status(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    results = []
    for key, meta in _PIPELINE_META.items():
        last_run = None
        records_stored = 0

        if meta["source_enum"]:
            latest = (
                db.query(ClimateReading)
                .filter(ClimateReading.source == meta["source_enum"])
                .order_by(ClimateReading.created_at.desc())
                .first()
            )
            if latest:
                last_run = latest.created_at.isoformat()
                records_stored = (
                    db.query(ClimateReading)
                    .filter(ClimateReading.source == meta["source_enum"])
                    .count()
                )

        results.append(
            {
                "source": key,
                "label": meta["label"],
                "type": meta["type"],
                "description": meta["description"],
                "can_trigger": meta["can_trigger"],
                "last_run": last_run,
                "records_stored": records_stored,
                "status": "ok" if last_run else "never",
            }
        )

    return results


async def _run_source_for_all_states(source_key: str) -> None:
    db = SessionLocal()
    try:
        states = db.query(State).order_by(State.name).all()
        for state in states:
            try:
                if source_key == "open_meteo":
                    await open_meteo.fetch_and_store(state.id, state.latitude, state.longitude, db)
                elif source_key == "nasa_power":
                    await nasa_power.fetch_and_store(state.id, state.latitude, state.longitude, db)
                elif source_key == "noaa_cdo":
                    await noaa_cdo.fetch_and_store(state.id, state.code, db)
            except Exception as exc:
                logger.error("Pipeline %s error for %s: %s", source_key, state.name, exc)
        db.commit()
        logger.info("Pipeline run complete for source: %s", source_key)
    finally:
        db.close()


@router.post("/pipeline/trigger/{source_key}", status_code=status.HTTP_202_ACCEPTED)
async def trigger_pipeline(
    source_key: str,
    background_tasks: BackgroundTasks,
    _: User = Depends(require_admin),
):
    if source_key not in _PIPELINE_META or not _PIPELINE_META[source_key]["can_trigger"]:
        raise HTTPException(
            status_code=400,
            detail=f"Source '{source_key}' cannot be triggered manually",
        )
    background_tasks.add_task(asyncio.ensure_future, _run_source_for_all_states(source_key))
    label = _PIPELINE_META[source_key]["label"]
    return {"message": f"Ingestion started for {label} across all 37 states", "source": source_key}
