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
    🔥 Unified pricing logic for campaign page
    """

    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id
    ).first()

    if not campaign:
        raise ValueError("Campaign not found")

    brackets = (
        db.query(DiscountBracket)
        .filter(DiscountBracket.campaign_id == campaign_id)
        .order_by(DiscountBracket.required_commitments.asc())
        .all()
    )

    if not brackets:
        return {
            "current_price": campaign.current_price,
            "brackets": [],
            "next_price": None,
            "buyers_needed": None
        }

    current_price = campaign.current_price
    next_price = None
    buyers_needed = None

    formatted_brackets = []

    for b in brackets:

        unlocked = buyers_joined >= b.required_commitments

        if unlocked:
            current_price = b.price
        elif next_price is None:
            next_price = b.price
            buyers_needed = b.required_commitments - buyers_joined

        formatted_brackets.append({
            "required_commitments": b.required_commitments,
            "price": b.price,
            "unlocked": unlocked
        })

    return {
        "current_price": current_price,
        "brackets": formatted_brackets,
        "next_price": next_price,
        "buyers_needed": buyers_needed
    }