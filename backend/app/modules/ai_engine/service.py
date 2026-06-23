import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.risk_assessment import RiskAssessment
from app.models.state import State
from app.modules.ai_engine.client import assess_state
from app.modules.ai_engine.context import build_full_context

logger = logging.getLogger(__name__)


async def run_assessment(state_id: str, db: Session) -> RiskAssessment:
    state = db.query(State).filter(State.id == state_id).first()
    if not state:
        raise ValueError(f"State not found: {state_id}")

    ctx = build_full_context(state.id, state.name, db)

    result = await assess_state(
        state_name=ctx["state_name"],
        climate_data=ctx["climate_data"],
        recent_assessments=ctx["recent_assessments"],
        active_disease_alerts=ctx["active_disease_alerts"],
        facility_summary=ctx["facility_summary"],
    )

    assessment = RiskAssessment(
        state_id=state.id,
        risk_level=result.risk_level,
        overall_score=result.overall_score,
        climate_score=result.climate_score,
        health_score=result.health_score,
        vulnerability_score=result.vulnerability_score,
        advisory_en=result.advisory_en,
        advisory_ha=result.advisory_ha,
        advisory_yo=result.advisory_yo,
        advisory_ig=result.advisory_ig,
        raw_response=result.model_dump(),
        assessed_at=datetime.now(timezone.utc),
    )
    db.add(assessment)

    state.current_risk_level = result.risk_level
    db.commit()

    logger.info(
        "Assessment complete for %s: %s (score=%.1f)",
        state.name, result.risk_level, result.overall_score,
    )
    return assessment
