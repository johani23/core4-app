# ====================================================================
# 💚 Core4.AI – Pricing Simulation Engine
# ====================================================================

from services.campaign_growth import compute_pricing_state


def simulate_campaign_growth(
    db,
    campaign_id: int,
    max_buyers: int = 120
):
    """
    Simulates buyer growth and pricing evolution.
    """

    results = []

    for buyers in range(1, max_buyers + 1):

        pricing = compute_pricing_state(
            db=db,
            campaign_id=campaign_id,
            buyers_joined=buyers
        )

        # -------------------------------------------------
        # Simulate conversion probability
        # -------------------------------------------------
        # Lower price → higher conversion
        if pricing["current_price"] is None:
            conversion_score = 0.2
        else:
            conversion_score = min(1.0, 1000 / (pricing["current_price"] + 1))

        # -------------------------------------------------
        # Momentum heuristic
        # -------------------------------------------------
        momentum = "low"
        if conversion_score > 0.7:
            momentum = "high"
        elif conversion_score > 0.4:
            momentum = "medium"

        results.append({
            "buyers": buyers,
            "current_price": pricing["current_price"],
            "next_price": pricing["next_price"],
            "buyers_needed": pricing["buyers_needed"],
            "conversion_score": round(conversion_score, 2),
            "momentum": momentum
        })

    return results