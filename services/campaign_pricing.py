# ====================================================================
# 💚 Core4.AI – Campaign Pricing Service (NEW)
# ====================================================================

from sqlalchemy.orm import Session
from sqlalchemy import func

from commitment.models import MarketCommitment as Commitment
from models.discount_bracket import DiscountBracket
from models.campaign import Campaign


def compute_pricing_state(db: Session, campaign_id: int, buyers_joined: int):
    """
    🔥 Unified pricing logic (PRODUCTION SAFE)
    """

    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id
    ).first()

    if not campaign:
        raise ValueError("Campaign not found")

    retail_price = campaign.retail_price or 0

    brackets = (
        db.query(DiscountBracket)
        .filter(DiscountBracket.campaign_id == campaign_id)
        .order_by(DiscountBracket.required_commitments.asc())
        .all()
    )

    # =========================================================
    # ✅ NO BRACKETS (SAFE FALLBACK)
    # =========================================================
    if not brackets:
        return {
            "current_price": retail_price,
            "brackets": [],
            "next_price": None,
            "buyers_needed": 0   # 🔥 FIX (never None)
        }

    current_price = retail_price
    next_price = None
    buyers_needed = 0

    formatted_brackets = []

    for b in brackets:

        required = b.required_commitments or 0
        price = b.price or retail_price

        unlocked = buyers_joined >= required

        if unlocked:
            current_price = price
        elif next_price is None:
            next_price = price
            buyers_needed = max(required - buyers_joined, 0)

        formatted_brackets.append({
            "required_commitments": required,
            "price": price,
            "unlocked": unlocked
        })

    return {
        "current_price": current_price,
        "brackets": formatted_brackets,
        "next_price": next_price,
        "buyers_needed": buyers_needed  # 🔥 ALWAYS INT
    }