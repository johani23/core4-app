# ============================================================================
# 💚 Core4AI – Governance Metrics API
# ----------------------------------------------------------------------------
# Dashboard & board-level metrics
# Read-only
# ============================================================================

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from db import get_db
from governance.metrics import get_governance_metrics
from utils.logger import log_event

router = APIRouter(
    prefix="/api/governance/metrics",
    tags=["governance"]
)

@router.get("/")
def governance_metrics(
    request: Request,
    db: Session = Depends(get_db),
):
    metrics = get_governance_metrics(db)

    log_event(
        request,
        action="governance_metrics_viewed",
        status="success",
        extra={
            "signals": metrics["signals"]["total"],
            "proposals": metrics["proposals"]["total"],
            "reviews": metrics["reviews"]["total"],
        }
    )

    return metrics
