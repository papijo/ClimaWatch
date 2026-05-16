from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.active_alert import ActiveAlert
from app.models.disease_alert import DiseaseAlert
from app.models.health_facility import HealthFacility
from app.models.risk_assessment import RiskAssessment
from app.models.state import State

router = APIRouter(prefix="/api", tags=["public"])


@router.get("/states")
def list_states(db: Session = Depends(get_db)):
    return db.query(State).order_by(State.name).all()


@router.get("/states/{state_id}")
def get_state(state_id: str, db: Session = Depends(get_db)):
    state = db.query(State).filter(State.id == state_id).first()
    if not state:
        raise HTTPException(status_code=404, detail="State not found")
    return state


@router.get("/states/{state_id}/lgas")
def get_state_lgas(state_id: str, db: Session = Depends(get_db)):
    from app.models.lga_vulnerability_score import LGAVulnerabilityScore
    return (
        db.query(LGAVulnerabilityScore)
        .filter(LGAVulnerabilityScore.state_id == state_id)
        .order_by(LGAVulnerabilityScore.vulnerability_score.desc())
        .all()
    )


@router.get("/facilities")
def list_facilities(
    state_id: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(HealthFacility)
    if state_id:
        q = q.filter(HealthFacility.state_id == state_id)
    return q.order_by(HealthFacility.name).all()


@router.get("/alerts/active")
def get_active_alerts(db: Session = Depends(get_db)):
    return (
        db.query(ActiveAlert)
        .filter(ActiveAlert.is_active.is_(True))
        .order_by(ActiveAlert.started_at.desc())
        .all()
    )


@router.get("/alerts/history")
def get_alert_history(
    cursor: str | None = None,
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(ActiveAlert).filter(ActiveAlert.is_active.is_(False))
    if cursor:
        q = q.filter(ActiveAlert.id < cursor)
    results = q.order_by(ActiveAlert.ended_at.desc()).limit(limit + 1).all()
    next_cursor = results[-1].id if len(results) > limit else None
    return {"items": results[:limit], "next_cursor": next_cursor}


@router.get("/disease-alerts")
def get_disease_alerts(db: Session = Depends(get_db)):
    return (
        db.query(DiseaseAlert)
        .filter(DiseaseAlert.is_active.is_(True))
        .order_by(DiseaseAlert.reported_at.desc())
        .all()
    )


@router.get("/forecasts/{state_id}")
def get_forecasts(state_id: str, db: Session = Depends(get_db)):
    assessment = (
        db.query(RiskAssessment)
        .filter(RiskAssessment.state_id == state_id)
        .order_by(RiskAssessment.assessed_at.desc())
        .first()
    )
    if not assessment:
        raise HTTPException(status_code=404, detail="No assessment found for this state")
    return assessment
