# ====================================================================
# 💚 Core4.AI – Intelligent Discount Bracket Generator (OPTIMIZED)
# ====================================================================

from sqlalchemy.orm import Session
from models.discount_bracket import DiscountBracket


# =====================================================
# LADDER STRATEGY ENGINE
# =====================================================
def _get_ladder_strategy(base_price: float, category: str | None = None):
    """
    Returns threshold + discount strategy based on:
    - price band
    - optional category tuning

    Designed for:
    - early activation
    - smooth momentum
    - no dead zones
    """

    category = (category or "").strip().lower()

    # -------------------------------------------------
    # HIGH VALUE ELECTRONICS (SAFE + CONTROLLED)
    # -------------------------------------------------
    if category in {"electronics", "devices", "appliances"} and base_price > 1000:
        return [
            (10, 0.97),
            (25, 0.95),
            (50, 0.93),   # reduced gap
            (90, 0.90),
        ]

    # -------------------------------------------------
    # LOW PRICE → FAST VIRAL LOOP
    # -------------------------------------------------
    if base_price < 200:
        return [
            (3, 0.97),    # early hook
            (10, 0.93),
            (25, 0.88),
            (50, 0.80),
        ]

    # -------------------------------------------------
    # MID PRICE → BALANCED GROWTH (OPTIMIZED)
    # -------------------------------------------------
    if base_price <= 1000:
        return [
            (5, 0.97),    # early activation
            (15, 0.94),
            (30, 0.90),   # removed dead zone
            (60, 0.85),
        ]

    # -------------------------------------------------
    # HIGH PRICE → SAFE PROGRESSION
    # -------------------------------------------------
    return [
        (8, 0.98),
        (20, 0.95),
        (45, 0.92),
        (80, 0.88),
    ]


# =====================================================
# MAIN GENERATOR
# =====================================================
def generate_default_brackets(
    db: Session,
    campaign_id: int,
    base_price: float,
    category: str | None = None,
):
    """
    Auto-create an intelligent pricing ladder for a campaign.

    Features:
    - Prevents duplicates
    - Adapts to price band
    - Smooth growth progression
    """

    # -------------------------------------------------
    # 🚨 SAFETY: prevent duplicate brackets
    # -------------------------------------------------
    existing = db.query(DiscountBracket).filter(
        DiscountBracket.campaign_id == campaign_id
    ).first()

    if existing:
        return []

    # -------------------------------------------------
    # Resolve ladder strategy
    # -------------------------------------------------
    ladder = _get_ladder_strategy(
        base_price=base_price,
        category=category,
    )

    brackets = []

    # -------------------------------------------------
    # Create brackets
    # -------------------------------------------------
    for idx, (threshold, multiplier) in enumerate(ladder):

        price = round(base_price * multiplier, 2)

        bracket = DiscountBracket(
            campaign_id=campaign_id,
            required_commitments=threshold,
            price=price,
            rank=idx,
        )

        db.add(bracket)
        brackets.append(bracket)

    db.commit()

    return brackets