# ============================================================================
# 💚 Core4.AI — Governance Feature Flags
# ============================================================================
# IMPORTANT:
# - observe = decisions are evaluated + logged ONLY
# - enforce = decisions can affect user flow (DISABLED in Beta Hardening)
# ============================================================================

# Allowed values: "observe", "enforce"
GOVERNANCE_MODE = "observe"

# Safety guard — never enable enforce without explicit override
ALLOW_ENFORCEMENT = False
