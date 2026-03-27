# ============================================================================
# 💚 Core4.AI – Campaign Model (FINAL CLEAN)
# ============================================================================

from sqlalchemy import Column, Integer, String, DateTime, Float, Index
from sqlalchemy.sql import func
from db import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)

    # relations
    product_id = Column(Integer, nullable=True)
    intention_id = Column(Integer, nullable=True)

    # decision
    channel = Column(String(100), nullable=False)
    context_note = Column(String(255), nullable=True)

    # required market fields
    slug = Column(String(120), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)

    retail_price = Column(Float, nullable=True)
    current_price = Column(Float, nullable=True)

    target_buyers = Column(Integer, default=100, nullable=False)

    status = Column(String(50), default="نشطة", index=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_campaign_status_created", "status", "created_at"),
    )