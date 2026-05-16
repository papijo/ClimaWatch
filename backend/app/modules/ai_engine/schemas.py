from pydantic import BaseModel, Field


class RiskAssessmentResponse(BaseModel):
    risk_level: str = Field(..., pattern="^(LOW|MODERATE|HIGH|CRITICAL)$")
    overall_score: float = Field(..., ge=0, le=100)
    climate_score: float = Field(..., ge=0, le=100)
    health_score: float = Field(..., ge=0, le=100)
    vulnerability_score: float = Field(..., ge=0, le=100)
    advisory_en: str
    advisory_ha: str
    advisory_yo: str
    advisory_ig: str
    key_drivers: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
