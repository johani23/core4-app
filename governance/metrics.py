# ============================================================================
# 💚 Core4AI — Governance Metrics Service
# ----------------------------------------------------------------------------
# Read-only aggregation for dashboards & board reporting
# ============================================================================

from sqlalchemy.orm import Session
from sqlalchemy import func

from models.signal import Signal
from models.governance_decision import GovernanceDecision
from models.governance_review import GovernanceReview


def get_governance_metrics(db: Session):
    """
    Aggregate governance-related metrics.
    Read-only. No side effects.
    """

    metrics = {}

    # ----------------------------------------------------------------------
    # Signals
    # ----------------------------------------------------------------------
    metrics["signals"] = {
        "total": db.query(func.count(Signal.id)).scalar(),
        "by_type": dict(
            db.query(
                Signal.signal_type,
                func.count(Signal.id)
            ).group_by(Signal.signal_type).all()
        ),
    }

    # ----------------------------------------------------------------------
    # Governance Decisions (Proposals)
    # ----------------------------------------------------------------------
    metrics["proposals"] = {
        "total": db.query(func.count(GovernanceDecision.id)).scalar(),
        "governor_required": db.query(
            func.count(GovernanceDecision.id)
        ).filter(
            GovernanceDecision.governor_required.is_(True)
        ).scalar(),
        "by_scenario": dict(
            db.query(
                GovernanceDecision.scenario,
                func.count(GovernanceDecision.id)
            ).group_by(GovernanceDecision.scenario).all()
        ),
    }

    # ----------------------------------------------------------------------
    # Governance Reviews (Human Actions)
    # ----------------------------------------------------------------------
    metrics["reviews"] = {
        "total": db.query(func.count(GovernanceReview.id)).scalar(),
        "by_action": dict(
            db.query(
                GovernanceReview.review_action,
                func.count(GovernanceReview.id)
            ).group_by(GovernanceReview.review_action).all()
        ),
    }

    return metrics
