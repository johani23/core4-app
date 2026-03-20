# ============================================================================
# 🔌 Load Latest Tribe Signal for Product
# Governance + Demand Alignment (SAFE)
# ============================================================================

from sqlalchemy.orm import Session
from models.tribe_signal import TribeSignal


def load_latest_tribe_signal(product_id: str, db: Session) -> dict | None:
    """
    Loads latest Tribe signal for a product.

    IMPORTANT:
    - Governance signals are HARD constraints.
    - Demand alignment signals are DESCRIPTIVE only.
    - This function must NEVER mandate a channel or influencer.
    """

    signal = (
        db.query(TribeSignal)
        .filter(TribeSignal.product_id == product_id)
        .order_by(TribeSignal.evaluated_at.desc())
        .first()
    )

    if not signal:
        return None

    # ------------------------------------------------------------
    # Governance signals (non-negotiable)
    # ------------------------------------------------------------
    governance = {
        "eligibility_state": signal.eligibility_state,
        "value_per_year": signal.value_per_year,
        "regret_risk": signal.regret_risk,
    }

    # ------------------------------------------------------------
    # Demand alignment signals (guidance only)
    # ------------------------------------------------------------
    demand_alignment = None

    if signal.top_audience:
        demand_alignment = {
            "audience": signal.top_audience,  # e.g. "influencer_A"
            "expected_conversion": "مرتفع",
            "price_alignment": "متوافق مع القيمة",
            "confidence": "عالية",
        }

    return {
        # HARD
        "governance": governance,

        # SOFT (guidance only)
        "demand_alignment": demand_alignment,
    }
