# ============================================================================
# 💚 Core4.AI – Campaign Model (PRODUCTION READY)
# ============================================================================

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, Index
from sqlalchemy.sql import func
from db import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)

    # -------------------------------------------------
    # Relations (soft-linked for MVP)
    # -------------------------------------------------
    product_id = Column(
        Integer,
        nullable=True
    )

    intention_id = Column(
        Integer,
        nullable=True
    )

    # -------------------------------------------------
    # Campaign decision (MERCHANT-OWNED)
    # -------------------------------------------------
    channel = Column(
        String(100),
        nullable=False,
        doc="Channel chosen by merchant (e.g. Influencer content, Ads, Organic)"
    )

    context_note = Column(
        String(255),
        nullable=True,
        doc="Non-binding analytical context at time of decision"
    )

    # -------------------------------------------------
    # Market Data (Needed for Referral Loop UI)
    # -------------------------------------------------

    slug = Column(
        String(120),
        unique=True,
        index=True,
        nullable=False   # 🔥 FIXED
    )

    title = Column(
        String(255),
        nullable=False   # 🔥 FIXED
    )

    retail_price = Column(
        Float,
        nullable=True
    )

    current_price = Column(
        Float,
        nullable=True
    )

    target_buyers = Column(
        Integer,
        default=100,
        nullable=False
    )

    # -------------------------------------------------
    # Status & audit
    # -------------------------------------------------

    status = Column(
        String(50),
        default="نشطة",
        index=True   # 🔥 FIXED
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # -------------------------------------------------
    # Indexes (performance critical)
    # -------------------------------------------------
    __table_args__ = (
        # ⚡ fast feed queries (active campaigns sorted by newest)
        Index("ix_campaign_status_created", "status", "created_at"),
    )