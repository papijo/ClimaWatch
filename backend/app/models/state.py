import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Float, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

RiskLevel = Enum("LOW", "MODERATE", "HIGH", "CRITICAL", name="risk_level")


class State(Base):
    __tablename__ = "states"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    region: Mapped[str] = mapped_column(String(50), nullable=False)
    capital: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    current_risk_level: Mapped[str] = mapped_column(RiskLevel, nullable=False, default="LOW")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    climate_readings: Mapped[list["ClimateReading"]] = relationship(back_populates="state")
    risk_assessments: Mapped[list["RiskAssessment"]] = relationship(back_populates="state")
    risk_state_changes: Mapped[list["RiskStateChange"]] = relationship(back_populates="state")
    active_alerts: Mapped[list["ActiveAlert"]] = relationship(back_populates="state")
    government_contacts: Mapped[list["GovernmentContact"]] = relationship(back_populates="state")
    user_subscriptions: Mapped[list["UserSubscription"]] = relationship(back_populates="state")
    health_facilities: Mapped[list["HealthFacility"]] = relationship(back_populates="state")
    lga_vulnerability_scores: Mapped[list["LGAVulnerabilityScore"]] = relationship(back_populates="state")
    disease_alerts: Mapped[list["DiseaseAlert"]] = relationship(back_populates="state")
