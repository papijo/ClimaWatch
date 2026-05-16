import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

RiskLevel = Enum("LOW", "MODERATE", "HIGH", "CRITICAL", name="risk_level", create_constraint=False)


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    state_id: Mapped[str] = mapped_column(String(36), ForeignKey("states.id", ondelete="CASCADE"), nullable=False, index=True)
    risk_level: Mapped[str] = mapped_column(RiskLevel, nullable=False)
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    climate_score: Mapped[float] = mapped_column(Float, nullable=False)
    health_score: Mapped[float] = mapped_column(Float, nullable=False)
    vulnerability_score: Mapped[float] = mapped_column(Float, nullable=False)
    advisory_en: Mapped[str | None] = mapped_column(Text)
    advisory_ha: Mapped[str | None] = mapped_column(Text)
    advisory_yo: Mapped[str | None] = mapped_column(Text)
    advisory_ig: Mapped[str | None] = mapped_column(Text)
    raw_response: Mapped[dict | None] = mapped_column(JSON)
    assessed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    state: Mapped["State"] = relationship(back_populates="risk_assessments")
