# ============================================================================
# 💚 Core4.AI — Governance Debug API
# Purpose:
# - Expose rule-level explainability
# - Internal / Admin / Governor use
# ============================================================================
from fastapi import APIRouter

from app.engines.governance.rule_debugger import debug_rules

router = APIRouter(
    prefix="/governance",
    tags=["Governance Debug"]
)

# ---------------------------------------------------------------------------
# POST /api/governance/debug
# ---------------------------------------------------------------------------
@router.post("/debug")
def debug_governance_rules(payload: dict):
    """
    Payload = signals dict
    Example:
    {
      "action_frequency": 6,
      "time_compression": 0.7,
      "deviation_score": 0.8
    }
    """

    return debug_rules(payload)
