import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

RiskLevel = Enum("LOW", "MODERATE", "HIGH", "CRITICAL", name="risk_level", create_constraint=False)


class RiskStateChange(Base):
    __tablename__ = "risk_state_changes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    state_id: Mapped[str] = mapped_column(String(36), ForeignKey("states.id", ondelete="CASCADE"), nullable=False, index=True)
    from_level: Mapped[str] = mapped_column(RiskLevel, nullable=False)
    to_level: Mapped[str] = mapped_column(RiskLevel, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    state: Mapped["State"] = relationship(back_populates="risk_state_changes")
