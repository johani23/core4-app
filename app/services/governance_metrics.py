# ============================================================================
# 💚 Core4.AI — Governance Metrics Service
# Purpose:
# - Compute lightweight governance KPIs
# - Read-only, no side effects
# ============================================================================
from sqlalchemy.orm import Session

from models.governance_decision import GovernanceDecision
from models.governance_review import GovernanceReview


def compute_governance_metrics(db: Session) -> dict:
    total_decisions = db.query(GovernanceDecision).count()
    requires_governor = (
        db.query(GovernanceDecision)
        .filter(GovernanceDecision.governor_required == True)
        .count()
    )

    reviewed = db.query(GovernanceReview).count()
    overrides = (
        db.query(GovernanceReview)
        .filter(GovernanceReview.review_action == "override")
        .count()
    )

    return {
        "total_decisions": total_decisions,
        "decisions_requiring_governor": requires_governor,
        "reviews_completed": reviewed,
        "overrides": overrides,
        "override_rate": (
            round(overrides / reviewed, 2) if reviewed > 0 else 0.0
        )
    }
