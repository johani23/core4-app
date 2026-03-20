# ============================================================================
# 🛡 Tribe Pricing Governance — Hard Constraints Layer
# ============================================================================

def apply_tribe_constraints(
    base_price: float,
    tribe_signal: dict | None
) -> dict:
    """
    Returns hard pricing constraints imposed by Tribe governance.
    """

    # Defaults
    min_price = None
    allow_discounting = True

    if tribe_signal:
        if (
            tribe_signal.get("eligibility_state") == "trusted"
            and tribe_signal.get("value_per_year") == "high"
            and tribe_signal.get("regret_risk", 1) < 0.25
        ):
            # 🔒 Hard floor (anti race-to-bottom)
            min_price = round(base_price * 0.95, 2)
            allow_discounting = False

    return {
        "min_price": min_price,
        "allow_discounting": allow_discounting,
    }
