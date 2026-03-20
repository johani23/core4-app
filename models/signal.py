# ============================================================================
# 💚 Core4.AI – Signal Model (Clean Architecture Version)
# Demand / Interest / Intent Signals
# Product-linked • Ghost-safe • Minimal coupling
# ============================================================================

from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from db import Base


class Signal(Base):
    __tablename__ = "signals"

    # -----------------------------------------------------------------------
    # Primary Key
    # -----------------------------------------------------------------------
    id = Column(Integer, primary_key=True, index=True)

    # -----------------------------------------------------------------------
    # Product Reference
    # IMPORTANT: Must match Product.id type (Integer)
    # -----------------------------------------------------------------------
    post_id = Column(Integer, index=True, nullable=True)

    # -----------------------------------------------------------------------
    # Signal Classification
    # -----------------------------------------------------------------------
    signal_type = Column(
        String(50),
        nullable=False,
        default="demand"  # demand | attention | intent
    )

    intent = Column(
        String(50),
        nullable=False,
        default="interested"  # interested | conditional | other
    )

    # -----------------------------------------------------------------------
    # Confidence (engine-owned weighting)
    # -----------------------------------------------------------------------
    confidence = Column(
        Float,
        nullable=False,
        default=0.6
    )

    # -----------------------------------------------------------------------
    # Timestamp
    # -----------------------------------------------------------------------
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
