# ============================================================================
# 💚 Core4AI – Governance API (Human-in-the-Loop ENFORCED)
# ----------------------------------------------------------------------------
# - Immutable decision log
# - Mandatory human context
# - Auditable & GA-safe
# ============================================================================

from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from db import get_db
from models.governance_decision import GovernanceDecision
from utils.logger import log_event

router = APIRouter(
    prefix="/api/governance",
    tags=["governance"]
)

# ============================================================================
# CREATE GOVERNANCE DECISION (LOG ONLY — NO EXECUTION)
# ============================================================================
@router.post("/decisions")
def create_decision(
    request: Request,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
):
    """
    Create an immutable governance decision record.
    This does NOT execute anything.
    """

    # ------------------------------------------------------------------------
    # REQUIRED BY MODEL
    # ------------------------------------------------------------------------
    user_id = payload.get("user_id")
    signals = payload.get("signals")

    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    if not signals:
        raise HTTPException(status_code=400, detail="signals is required")

    # ------------------------------------------------------------------------
    # CREATE DECISION (FIELDS MATCH MODEL EXACTLY)
    # ------------------------------------------------------------------------
    try:
        decision = GovernanceDecision(
            user_id=user_id,
            scenario=payload.get("scenario"),
            scenario_id=payload.get("scenario_id"),
            signals=signals,
            triggered_signals=payload.get("triggered_signals"),
            action=payload.get("action"),
            governor_required=payload.get("governor_required", True),
            copy_key=payload.get("copy_key"),
            pilot_mode=payload.get("pilot_mode", True),
        )

        db.add(decision)
        db.commit()
        db.refresh(decision)

    except Exception as e:
        # expose real error once, not silent 500
        raise HTTPException(
            status_code=500,
            detail=f"Governance decision creation failed: {str(e)}"
        )

    # ------------------------------------------------------------------------
    # LOG EVENT
    # ------------------------------------------------------------------------
    log_event(
        request,
        action="governance_decision_logged",
        status="success",
        extra={
            "decision_id": decision.id,
            "user_id": decision.user_id,
            "scenario": decision.scenario,
            "governor_required": decision.governor_required,
        }
    )

    return {
        "status": "logged",
        "decision_id": decision.id,
        "governor_required": decision.governor_required,
        "request_id": getattr(request.state, "request_id", None),
    }
