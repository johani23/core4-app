# commitment/market_models.py

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime,
    Boolean, Float, ForeignKey
)
from db import Base


# ============================================================
# Market Loop Commitment (ADVANCED ENGINE ONLY)
# Separate table to avoid conflict with main commitment engine
# ============================================================

class MarketLoopCommitment(Base):
    __tablename__ = "market_loop_commitments"  # ✅ IMPORTANT: different table

    id = Column(Integer, primary_key=True, index=True)

    market_intention_id = Column(
        Integer,
        ForeignKey("market_intentions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    buyer_id = Column(String(64), index=True, nullable=False)

    quantity = Column(Integer, default=1, nullable=False)

    commitment_type = Column(String(16), default="SOFT", nullable=False)

    weight = Column(Float, default=1.0, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)