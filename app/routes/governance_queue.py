# ============================================================================
# 💚 Core4.AI — Governance Review Queue (Beta Hardening)
# API-only. No UI. No enforcement.
# ============================================================================
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from db import get_db
from models.governance_decision import GovernanceDecision
from models.governance_review import GovernanceReview

router = APIRouter(
    prefix="/governance",
    tags=["Governance Queue"]
)

# ---------------------------------------------------------------------------
# GET /api/governance/queue
# ---------------------------------------------------------------------------
@router.get("/queue")
def get_governance_queue(db: Session = Depends(get_db)):
    """
    Returns decisions that require human governor review
    and have not been reviewed yet.
    """

    subquery = db.query(GovernanceReview.decision_id).subquery()

    pending = (
        db.query(GovernanceDecision)
        .filter(GovernanceDecision.governor_required == True)
        .filter(~GovernanceDecision.id.in_(subquery))
        .order_by(GovernanceDecision.created_at.asc())
        .all()
    )

    return {
        "count": len(pending),
        "pending_reviews": [
            {
                "decision_id": d.id,
                "user_id": d.user_id,
                "scenario": d.scenario,
                "action": d.action,
                "created_at": d.created_at
            }
            for d in pending
        ]
    }


# ---------------------------------------------------------------------------
# POST /api/governance/decision/{id}/review
# ---------------------------------------------------------------------------
@router.post("/decision/{decision_id}/review")
def review_governance_decision(
    decision_id: int,
    payload: dict,
    db: Session = Depends(get_db)
):
    """
    Human governor reviews a decision.
    Payload:
    {
        "governor_id": "G-123",
        "review_action": "confirm | override | defer",
        "reason": "optional explanation"
    }
    """

    decision = (
        db.query(GovernanceDecision)
        .filter(GovernanceDecision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    review = GovernanceReview(
        decision_id=decision_id,
        governor_id=payload.get("governor_id"),
        review_action=payload.get("review_action"),
        reason=payload.get("reason"),
        reviewed_at=datetime.utcnow()
    )

    db.add(review)
    db.commit()

    return {
        "status": "review_recorded",
        "decision_id": decision_id,
        "review_action": review.review_action
    }
