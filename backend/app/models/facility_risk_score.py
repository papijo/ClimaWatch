import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FacilityRiskScore(Base):
    __tablename__ = "facility_risk_scores"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    facility_id: Mapped[str] = mapped_column(String(36), ForeignKey("health_facilities.id", ondelete="CASCADE"), nullable=False, index=True)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    flood_risk: Mapped[float] = mapped_column(Float, nullable=False)
    heat_stress_risk: Mapped[float] = mapped_column(Float, nullable=False)
    disease_burden_risk: Mapped[float] = mapped_column(Float, nullable=False)
    infrastructure_vulnerability: Mapped[float] = mapped_column(Float, nullable=False)
    scored_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    facility: Mapped["HealthFacility"] = relationship(back_populates="risk_scores")
