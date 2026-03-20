# ====================================================================
# 🚀 Core4.AI – Growth Event Model
# Tracks activation + growth loop signals
# ====================================================================

from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from db import Base


class GrowthEvent(Base):
    __tablename__ = "growth_events"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, nullable=True, index=True)

    event_type = Column(
        String(50),
        nullable=False,
        index=True
    )

    metadata = Column(
        JSON,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )