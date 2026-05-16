import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

DiseaseAlertLevel = Enum("watch", "warning", "emergency", name="disease_alert_level")
DiseaseAlertSource = Enum("ncdc", "who_afro", name="disease_alert_source")


class DiseaseAlert(Base):
    __tablename__ = "disease_alerts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    state_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("states.id", ondelete="SET NULL"), index=True)
    disease_name: Mapped[str] = mapped_column(String(200), nullable=False)
    alert_level: Mapped[str] = mapped_column(DiseaseAlertLevel, nullable=False)
    source: Mapped[str] = mapped_column(DiseaseAlertSource, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    affected_lgas: Mapped[list | None] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    reported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    state: Mapped["State | None"] = relationship(back_populates="disease_alerts")
