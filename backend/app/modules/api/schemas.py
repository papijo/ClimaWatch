from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StateListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    code: str
    region: str
    capital: str
    latitude: float
    longitude: float
    current_risk_level: str


class LatestAssessmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    risk_level: str
    overall_score: float
    climate_score: float
    health_score: float
    vulnerability_score: float
    advisory_en: str | None = None
    advisory_ha: str | None = None
    advisory_yo: str | None = None
    advisory_ig: str | None = None
    assessed_at: datetime


class StateDetailOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    code: str
    region: str
    capital: str
    latitude: float
    longitude: float
    current_risk_level: str
    latest_assessment: LatestAssessmentOut | None = None


class LGAScoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    state_id: str
    lga_name: str
    vulnerability_score: float
    population_density_score: float
    health_access_score: float
    climate_exposure_score: float
    scored_at: datetime


class FacilityRiskScoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    risk_score: float
    flood_risk: float
    heat_stress_risk: float
    disease_burden_risk: float
    infrastructure_vulnerability: float
    scored_at: datetime


class FacilityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    state_id: str
    lga: str
    name: str
    facility_type: str
    ownership: str
    category: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    latest_risk_score: FacilityRiskScoreOut | None = None


class ActiveAlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    state_id: str
    title: str
    description: str
    risk_level: str
    is_active: bool
    started_at: datetime
    ended_at: datetime | None = None


class AlertHistoryResponse(BaseModel):
    items: list[ActiveAlertOut]
    next_cursor: str | None = None


class DiseaseAlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    state_id: str | None = None
    disease_name: str
    alert_level: str
    source: str
    description: str
    affected_lgas: list | None = None
    is_active: bool
    reported_at: datetime


class ForecastOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    state_id: str
    risk_level: str
    overall_score: float
    climate_score: float
    health_score: float
    vulnerability_score: float
    advisory_en: str | None = None
    advisory_ha: str | None = None
    advisory_yo: str | None = None
    advisory_ig: str | None = None
    key_drivers: list[str] | None = None
    recommended_actions: list[str] | None = None
    assessed_at: datetime
