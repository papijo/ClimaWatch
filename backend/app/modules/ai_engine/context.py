from sqlalchemy.orm import Session

from app.models.climate_reading import ClimateReading
from app.models.disease_alert import DiseaseAlert
from app.models.facility_risk_score import FacilityRiskScore
from app.models.health_facility import HealthFacility
from app.models.risk_assessment import RiskAssessment


def get_latest_climate(state_id: str, db: Session) -> dict:
    readings = (
        db.query(ClimateReading)
        .filter(ClimateReading.state_id == state_id)
        .order_by(ClimateReading.recorded_at.desc())
        .limit(3)
        .all()
    )
    if not readings:
        return {"status": "no_data"}

    merged: dict = {}
    for r in readings:
        if r.temperature_celsius is not None and "temperature_celsius" not in merged:
            merged["temperature_celsius"] = r.temperature_celsius
        if r.humidity_percent is not None and "humidity_percent" not in merged:
            merged["humidity_percent"] = r.humidity_percent
        if r.rainfall_mm is not None and "rainfall_mm" not in merged:
            merged["rainfall_mm"] = r.rainfall_mm
        if r.wind_speed_kmh is not None and "wind_speed_kmh" not in merged:
            merged["wind_speed_kmh"] = r.wind_speed_kmh
        if r.uv_index is not None and "uv_index" not in merged:
            merged["uv_index"] = r.uv_index
        if r.air_quality_index is not None and "air_quality_index" not in merged:
            merged["air_quality_index"] = r.air_quality_index

    merged["sources"] = list({r.source for r in readings})
    merged["recorded_at"] = readings[0].recorded_at.isoformat()
    return merged


def get_recent_assessments(state_id: str, db: Session, limit: int = 3) -> list[dict]:
    assessments = (
        db.query(RiskAssessment)
        .filter(RiskAssessment.state_id == state_id)
        .order_by(RiskAssessment.assessed_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "risk_level": a.risk_level,
            "overall_score": a.overall_score,
            "climate_score": a.climate_score,
            "health_score": a.health_score,
            "vulnerability_score": a.vulnerability_score,
            "assessed_at": a.assessed_at.isoformat(),
        }
        for a in assessments
    ]


def get_active_disease_alerts(state_id: str, db: Session) -> list[dict]:
    alerts = (
        db.query(DiseaseAlert)
        .filter(
            (DiseaseAlert.state_id == state_id) | (DiseaseAlert.state_id.is_(None)),
            DiseaseAlert.is_active.is_(True),
        )
        .all()
    )
    return [
        {
            "disease_name": a.disease_name,
            "alert_level": a.alert_level,
            "source": a.source,
            "description": a.description,
        }
        for a in alerts
    ]


def get_facility_summary(state_id: str, db: Session) -> dict:
    facilities = db.query(HealthFacility).filter(HealthFacility.state_id == state_id).all()
    if not facilities:
        return {"total": 0, "high_risk_count": 0, "avg_risk_score": None}

    facility_ids = [f.id for f in facilities]
    scores = (
        db.query(FacilityRiskScore)
        .filter(FacilityRiskScore.facility_id.in_(facility_ids))
        .all()
    )

    high_risk = sum(1 for s in scores if s.risk_score >= 60)
    avg_score = sum(s.risk_score for s in scores) / len(scores) if scores else None

    return {
        "total": len(facilities),
        "by_type": _count_by(facilities, "facility_type"),
        "by_ownership": _count_by(facilities, "ownership"),
        "high_risk_count": high_risk,
        "avg_risk_score": round(avg_score, 1) if avg_score else None,
    }


def build_full_context(state_id: str, state_name: str, db: Session) -> dict:
    return {
        "state_name": state_name,
        "climate_data": get_latest_climate(state_id, db),
        "recent_assessments": get_recent_assessments(state_id, db),
        "active_disease_alerts": get_active_disease_alerts(state_id, db),
        "facility_summary": get_facility_summary(state_id, db),
    }


def _count_by(items: list, attr: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        val = getattr(item, attr, "unknown")
        counts[val] = counts.get(val, 0) + 1
    return counts
