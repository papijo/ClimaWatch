from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.active_alert import ActiveAlert
from app.models.disease_alert import DiseaseAlert
from app.models.facility_risk_score import FacilityRiskScore
from app.models.health_facility import HealthFacility
from app.models.lga_vulnerability_score import LGAVulnerabilityScore
from app.models.risk_assessment import RiskAssessment
from app.models.state import State
from app.modules.api.schemas import (
    ActiveAlertOut,
    AlertHistoryResponse,
    DiseaseAlertOut,
    FacilityOut,
    FacilityRiskScoreOut,
    ForecastOut,
    LGAScoreOut,
    StateDetailOut,
    StateListItem,
    LatestAssessmentOut,
)

router = APIRouter(prefix="/api", tags=["public"])


@router.get("/states", response_model=list[StateListItem])
def list_states(db: Session = Depends(get_db)):
    return db.query(State).order_by(State.name).all()


@router.get("/states/{state_id}", response_model=StateDetailOut)
def get_state(state_id: str, db: Session = Depends(get_db)):
    state = db.query(State).filter(State.id == state_id).first()
    if not state:
        raise HTTPException(status_code=404, detail="State not found")

    latest = (
        db.query(RiskAssessment)
        .filter(RiskAssessment.state_id == state_id)
        .order_by(RiskAssessment.assessed_at.desc())
        .first()
    )

    result = StateDetailOut.model_validate(state)
    if latest:
        result.latest_assessment = LatestAssessmentOut.model_validate(latest)
    return result


@router.get("/states/{state_id}/lgas", response_model=list[LGAScoreOut])
def get_state_lgas(state_id: str, db: Session = Depends(get_db)):
    return (
        db.query(LGAVulnerabilityScore)
        .filter(LGAVulnerabilityScore.state_id == state_id)
        .order_by(LGAVulnerabilityScore.vulnerability_score.desc())
        .all()
    )


@router.get("/facilities", response_model=list[FacilityOut])
def list_facilities(
    state_id: str | None = None,
    limit: int = Query(default=100, le=500),
    cursor: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(HealthFacility)
    if state_id:
        q = q.filter(HealthFacility.state_id == state_id)
    if cursor:
        q = q.filter(HealthFacility.id > cursor)
    facilities = q.order_by(HealthFacility.id).limit(limit).all()

    results = []
    for f in facilities:
        latest_score = (
            db.query(FacilityRiskScore)
            .filter(FacilityRiskScore.facility_id == f.id)
            .order_by(FacilityRiskScore.scored_at.desc())
            .first()
        )
        item = FacilityOut.model_validate(f)
        if latest_score:
            item.latest_risk_score = FacilityRiskScoreOut.model_validate(latest_score)
        results.append(item)

    return results


@router.get("/alerts/active", response_model=list[ActiveAlertOut])
def get_active_alerts(db: Session = Depends(get_db)):
    return (
        db.query(ActiveAlert)
        .filter(ActiveAlert.is_active.is_(True))
        .order_by(ActiveAlert.started_at.desc())
        .all()
    )


@router.get("/alerts/history", response_model=AlertHistoryResponse)
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
    return AlertHistoryResponse(
        items=results[:limit],
        next_cursor=next_cursor,
    )


@router.get("/disease-alerts", response_model=list[DiseaseAlertOut])
def get_disease_alerts(db: Session = Depends(get_db)):
    return (
        db.query(DiseaseAlert)
        .filter(DiseaseAlert.is_active.is_(True))
        .order_by(DiseaseAlert.reported_at.desc())
        .all()
    )


@router.get("/forecasts/{state_id}", response_model=ForecastOut)
def get_forecasts(state_id: str, db: Session = Depends(get_db)):
    assessment = (
        db.query(RiskAssessment)
        .filter(RiskAssessment.state_id == state_id)
        .order_by(RiskAssessment.assessed_at.desc())
        .first()
    )
    if not assessment:
        raise HTTPException(status_code=404, detail="No assessment found for this state")

    result = ForecastOut.model_validate(assessment)
    raw = assessment.raw_response or {}
    result.key_drivers = raw.get("key_drivers")
    result.recommended_actions = raw.get("recommended_actions")
    return result
