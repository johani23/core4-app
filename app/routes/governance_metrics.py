# ============================================================================
# 💚 Core4.AI — Governance Metrics API
# Purpose:
# - Expose governance KPIs for admins / ops
# ============================================================================
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import get_db
from app.services.governance_metrics import compute_governance_metrics

router = APIRouter(
    prefix="/governance",
    tags=["Governance Metrics"]
)

# ---------------------------------------------------------------------------
# GET /api/governance/metrics
# ---------------------------------------------------------------------------
@router.get("/metrics")
def get_governance_metrics(db: Session = Depends(get_db)):
    return compute_governance_metrics(db)
