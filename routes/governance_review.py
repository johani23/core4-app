# ============================================================================
# 💚 Core4AI – Governance Review API
# ----------------------------------------------------------------------------
# - Human governance review events
# - Non-breaking (no decision mutation)
# - Audit-grade
# ============================================================================

from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, Literal

from db import get_db
from models.governance_decision import GovernanceDecision
from models.governance_review import GovernanceReview
from utils.logger import log_event

router = APIRouter(
    prefix="/api/governance/reviews",
    tags=["governance"]
)

ReviewAction = Literal["confirm", "override", "defer"]

# ----------------------------------------------------------------------------
# CREATE GOVERNANCE REVIEW
# ----------------------------------------------------------------------------
@router.post("/")
def create_review(
    request: Request,
    decision_id: int,
    governor_id: str,
    review_action: ReviewAction,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
):
    decision = (
        db.query(GovernanceDecision)
        .filter(GovernanceDecision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(status_code=404, detail="Governance decision not found")

    review = GovernanceReview(
        decision_id=decision_id,
        governor_id=governor_id,
        review_action=review_action,
        reason=reason,
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    log_event(
        request,
        action="governance_review_logged",
        status=review_action,
        extra={
            "decision_id": decision_id,
            "governor_id": governor_id,
            "review_action": review_action,
        }
    )

    return {
        "status": "logged",
        "review_id": review.id,
        "decision_id": decision_id,
        "review_action": review_action,
        "request_id": getattr(request.state, "request_id", None),
    }


# ----------------------------------------------------------------------------
# LIST REVIEWS FOR A DECISION
# ----------------------------------------------------------------------------
@router.get("/{decision_id}")
def list_reviews(
    request: Request,
    decision_id: int,
    db: Session = Depends(get_db),
):
    reviews = (
        db.query(GovernanceReview)
        .filter(GovernanceReview.decision_id == decision_id)
        .order_by(GovernanceReview.reviewed_at.asc())
        .all()
    )

    return [
        {
            "review_id": r.id,
            "governor_id": r.governor_id,
            "review_action": r.review_action,
            "reason": r.reason,
            "reviewed_at": r.reviewed_at.isoformat(),
        }
        for r in reviews
    ]
