# ============================================================================
# 🟢 Core4.AI – Demand Signal Log
# One record per (MarketIntention x Merchant)
# Immutable visibility log for audit & marketplace fairness
# ============================================================================

from sqlalchemy import Column, Integer, DateTime, Boolean, ForeignKey
from datetime import datetime
from db import Base


class DemandSignalLog(Base):
    __tablename__ = "demand_signal_logs"

    id = Column(Integer, primary_key=True, index=True)

    market_intention_id = Column(
        Integer,
        ForeignKey("market_intentions.id"),
        nullable=False,
        index=True,
    )

    merchant_id = Column(Integer, index=True, nullable=False)

    visible = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
