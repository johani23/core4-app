# ============================================================================
# 💚 Core4.AI — Governance Decision Log (Pilot)
# Purpose:
# - Immutable audit trail
# - Explainability
# - Post-hoc analysis (regret, overrides, bias)
# ============================================================================
from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean
from datetime import datetime

from db import Base

class GovernanceDecision(Base):
    __tablename__ = "governance_decisions"

    id = Column(Integer, primary_key=True, index=True)

    # Who
    user_id = Column(String, index=True, nullable=False)

    # What triggered
    scenario = Column(String, index=True)
    scenario_id = Column(String, index=True)

    # Signals
    signals = Column(JSON, nullable=False)
    triggered_signals = Column(JSON, nullable=True)

    # Decision
    action = Column(String, nullable=True)
    governor_required = Column(Boolean, default=False)

    # Meta
    copy_key = Column(String, nullable=True)
    pilot_mode = Column(Boolean, default=True)

    # Time
    created_at = Column(DateTime, default=datetime.utcnow)
