# ============================================================================
# 💚 Core4.AI — Governance Mode Resolver
# Purpose:
# - Centralized read-only access to governance mode
# - Prevent accidental enforcement
# ============================================================================
from config.governance_flags import GOVERNANCE_MODE, ALLOW_ENFORCEMENT


def get_governance_mode():
    return GOVERNANCE_MODE


def enforcement_enabled():
    """
    Enforcement is allowed ONLY if:
    - mode == enforce
    - explicit safety flag is enabled
    """
    return GOVERNANCE_MODE == "enforce" and ALLOW_ENFORCEMENT is True
