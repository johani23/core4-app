# ====================================================================
# 🚀 Core4.AI – Growth Event Model (FINAL – CAMPAIGN READY)
# ====================================================================

from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from db import Base


class GrowthEvent(Base):
    __tablename__ = "growth_events"

    id = Column(Integer, primary_key=True, index=True)

    # -------------------------------------------------
    # Context
    # -------------------------------------------------
    user_id = Column(Integer, nullable=True, index=True)

    campaign_id = Column(               # ✅ REQUIRED FOR CAMPAIGN ANALYTICS
        Integer,
        ForeignKey("campaigns.id"),
        nullable=True,
        index=True
    )

    ref_code = Column(                  # ✅ REQUIRED FOR REFERRAL TRACKING
        String(64),
        nullable=True,
        index=True
    )

    # -------------------------------------------------
    # Event Type
    # -------------------------------------------------
    event_type = Column(
        String(50),
        nullable=False,
        index=True
    )

    # -------------------------------------------------
    # Flexible Metadata
    # -------------------------------------------------
    event_metadata = Column(
        JSON,
        nullable=True
    )

    # -------------------------------------------------
    # Timestamp
    # -------------------------------------------------
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True
    )