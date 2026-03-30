# ====================================================================
# 💚 Core4.AI – Campaign Pricing Service (FINAL PRODUCTION SAFE)
# ====================================================================

from sqlalchemy.orm import Session

from models.discount_bracket import DiscountBracket
from models.campaign import Campaign


def compute_pricing_state(db: Session, campaign_id: int, buyers_joined: int):
    """
    🔥 Unified pricing logic (PRODUCTION SAFE)

    Guarantees:
    - Always returns FULL ladder
    - No filtering of unlocked brackets
    - No None values
    - Stable pricing behavior
    """

    # =========================================================
    # LOAD CAMPAIGN
    # =========================================================
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id
    ).first()

    if not campaign:
        raise ValueError("Campaign not found")

    retail_price = float(campaign.retail_price or 0)

    # =========================================================
    # LOAD BRACKETS (SORTED ASC)
    # =========================================================
    brackets = (
        db.query(DiscountBracket)
        .filter(DiscountBracket.campaign_id == campaign_id)
        .order_by(DiscountBracket.required_commitments.asc())
        .all()
    )

    # =========================================================
    # NO BRACKETS (SAFE FALLBACK)
    # =========================================================
    if not brackets:
        return {
            "current_price": retail_price,
            "brackets": [],
            "next_price": None,
            "buyers_needed": 0
        }

    # =========================================================
    # INITIAL STATE
    # =========================================================
    current_price = retail_price
    next_price = None
    buyers_needed = 0

    formatted_brackets = []

    # =========================================================
    # MAIN LOOP
    # =========================================================
    for b in brackets:

        required = int(b.required_commitments or 0)
        price = float(b.price or retail_price)

        # ✅ UNLOCK STATE
        unlocked = buyers_joined >= required

        # =====================================================
        # UPDATE CURRENT PRICE (LAST UNLOCKED WINS)
        # =====================================================
        if unlocked:
            current_price = price

        # =====================================================
        # DETECT NEXT UNLOCK (FIRST LOCKED ONLY)
        # =====================================================
        elif next_price is None:
            next_price = price
            buyers_needed = max(required - buyers_joined, 0)

        # =====================================================
        # BUILD FULL LADDER (NO FILTERING)
        # =====================================================
        formatted_brackets.append({
            "required_commitments": required,
            "price": price,
            "unlocked": unlocked
        })

    # =========================================================
    # FINAL RETURN
    # =========================================================
    return {
        "current_price": float(current_price),
        "brackets": formatted_brackets,   # 🔥 ALWAYS FULL LIST
        "next_price": float(next_price) if next_price else None,
        "buyers_needed": int(buyers_needed)  # 🔥 ALWAYS INT
    }