# ============================================================================
# 🛡 Pricing Governance Engine — Tribe-Controlled Guardrails
# INTERNAL USE ONLY
# ============================================================================

def apply_tribe_pricing_guardrails(
    base_price: float,
    tribe_signal: dict | None
) -> dict:
    """
    Applies Tribe governance guardrails to pricing logic.

    IMPORTANT:
    - This function must NEVER expose numeric floors to UI or merchants.
    - Outputs are INTERNAL constraints only.
    """

    # Default: no governance constraints
    guardrail_active = False
    min_allowed_price = None
    discount_allowed = True
    governance_context = "free_market"

    if tribe_signal:
        if (
            tribe_signal.get("eligibility_state") == "trusted"
            and tribe_signal.get("value_per_year") == "high"
            and tribe_signal.get("regret_risk", 1) < 0.25
        ):
            guardrail_active = True
            min_allowed_price = round(base_price * 0.95, 2)
            discount_allowed = False
            governance_context = "trusted_tribe_guardrail"

    return {
        # 🔒 INTERNAL ONLY — do not expose
        "guardrail_active": guardrail_active,
        "min_allowed_price": min_allowed_price,
        "discount_allowed": discount_allowed,

        # SAFE DESCRIPTIVE CONTEXT
        "governance_context": governance_context,
    }
