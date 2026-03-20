# ============================================================================
# 💚 Core4AI — Governance Review Log
# Purpose:
# - Human review of governance decisions
# - Non-breaking extension (no change to decisions table)
# ============================================================================

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime

from db import Base


class GovernanceReview(Base):
    __tablename__ = "governance_reviews"

    id = Column(Integer, primary_key=True, index=True)

    # Link to decision
    decision_id = Column(Integer, ForeignKey("governance_decisions.id"), nullable=False)

    # Human reviewer
    governor_id = Column(String, nullable=False)
    review_action = Column(String, nullable=False)  # confirm | override | defer
    reason = Column(String, nullable=True)

    reviewed_at = Column(DateTime, default=datetime.utcnow)
