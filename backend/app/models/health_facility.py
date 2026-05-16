import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

FacilityType = Enum("primary", "secondary", "tertiary", name="facility_type")
FacilityOwnership = Enum("public", "private", "ngo", "faith_based", name="facility_ownership")


class HealthFacility(Base):
    __tablename__ = "health_facilities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    state_id: Mapped[str] = mapped_column(String(36), ForeignKey("states.id", ondelete="CASCADE"), nullable=False, index=True)
    lga: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    facility_type: Mapped[str] = mapped_column(FacilityType, nullable=False)
    ownership: Mapped[str] = mapped_column(FacilityOwnership, nullable=False)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    bed_count: Mapped[int | None] = mapped_column(Integer)
    source: Mapped[str] = mapped_column(String(50), nullable=False, default="nhfr")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    state: Mapped["State"] = relationship(back_populates="health_facilities")
    risk_scores: Mapped[list["FacilityRiskScore"]] = relationship(back_populates="facility")
