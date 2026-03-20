# ============================================================================
# 📁 System Events Table (Core4.AI)
# Used for economic triggers & audit trail
# ============================================================================

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON
from db import Base


class SystemEvent(Base):
    __tablename__ = "system_events"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)

    # Type of event (e.g., MARKET_BRACKET_UNLOCKED)
    event_type = Column(String(64), nullable=False)

    # JSON payload (market_intention_id, bracket_id, etc.)
    payload = Column(JSON, nullable=False)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)