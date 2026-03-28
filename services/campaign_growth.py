# ====================================================================
# 💚 Core4.AI – Campaign Growth Service (FINAL PRODUCTION)
# ====================================================================

from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from models.discount_bracket import DiscountBracket
from commitment.models import MarketCommitment


# =====================================================
# BUYER COUNT
# =====================================================

def count_buyers_joined(db: Session, campaign_id: int) -> int:
    return db.query(MarketCommitment).filter(
        MarketCommitment.campaign_id == campaign_id,
        MarketCommitment.is_active == True
    ).count()


# =====================================================
# 🧠 PRICING ENGINE (CORE)
# =====================================================

def compute_pricing_state(db: Session, campaign_id: int, buyers_joined: int):
    """
    Returns full pricing state:
    - current_price
    - next_price
    - buyers_needed
    - brackets
    """

    brackets = db.query(DiscountBracket).filter(
        DiscountBracket.campaign_id == campaign_id
    ).order_by(
        DiscountBracket.required_commitments.asc()
    ).all()

    # -------------------------------------------------
    # No brackets → safe fallback
    # -------------------------------------------------
    if not brackets:
        return {
            "current_price": None,
            "next_price": None,
            "buyers_needed": 0,
            "brackets": []
        }

    current_price = None
    next_price = None
    buyers_needed = 0
    bracket_states = []

    # -------------------------------------------------
    # Determine unlocked + next bracket
    # -------------------------------------------------
    for bracket in brackets:

        unlocked = buyers_joined >= bracket.required_commitments

        if unlocked:
            current_price = bracket.price

        elif next_price is None:
            next_price = bracket.price
            buyers_needed = bracket.required_commitments - buyers_joined

        bracket_states.append({
            "required_commitments": bracket.required_commitments,
            "price": bracket.price,
            "unlocked": unlocked
        })

    # -------------------------------------------------
    # Edge case: no unlock yet
    # -------------------------------------------------
    if current_price is None:
        current_price = brackets[0].price

    return {
        "current_price": current_price,
        "next_price": next_price,
        "buyers_needed": buyers_needed,
        "brackets": bracket_states
    }


# =====================================================
# NEXT UNLOCK (LEGACY COMPAT)
# =====================================================

def get_next_unlock(db: Session, campaign_id: int, buyers_joined: int):
    """
    Backward compatibility for existing UI.
    """
    state = compute_pricing_state(db, campaign_id, buyers_joined)
    return state["next_price"], state["buyers_needed"]


# =====================================================
# RECENT COUNTS
# =====================================================

def get_recent_counts(db: Session, campaign_id: int):
    now = datetime.utcnow()
    one_hour_ago = now - timedelta(hours=1)
    today_start = datetime(now.year, now.month, now.day)

    joined_today = db.query(MarketCommitment).filter(
        MarketCommitment.campaign_id == campaign_id,
        MarketCommitment.is_active == True,
        MarketCommitment.created_at >= today_start
    ).count()

    joined_last_hour = db.query(MarketCommitment).filter(
        MarketCommitment.campaign_id == campaign_id,
        MarketCommitment.is_active == True,
        MarketCommitment.created_at >= one_hour_ago
    ).count()

    return joined_today, joined_last_hour


# =====================================================
# RECENT JOINS
# =====================================================

def get_recent_joins(db: Session, campaign_id: int, limit: int = 10):
    return db.query(MarketCommitment).filter(
        MarketCommitment.campaign_id == campaign_id,
        MarketCommitment.is_active == True
    ).order_by(
        MarketCommitment.created_at.desc()
    ).limit(limit).all()


# =====================================================
# REFERRAL STATS
# =====================================================

def referral_stats(db: Session, campaign_id: int, ref_code: str):
    owner = db.query(MarketCommitment).filter(
        MarketCommitment.campaign_id == campaign_id,
        MarketCommitment.referral_code == ref_code,
        MarketCommitment.is_active == True
    ).first()

    if not owner:
        return {
            "campaign_id": campaign_id,
            "referral_code": ref_code,
            "exists": False,
            "owner_email": None,
            "owner_name": None,
            "total_referrals": 0,
            "recent_referrals": [],
            "last_joined_at": None
        }

    referrals = db.query(MarketCommitment).filter(
        MarketCommitment.campaign_id == campaign_id,
        MarketCommitment.referred_by == ref_code,
        MarketCommitment.is_active == True
    ).order_by(
        MarketCommitment.created_at.desc()
    ).all()

    recent_referrals = [
        {
            "email": r.email,
            "first_name": r.first_name,
            "city": r.city,
            "joined_at": r.created_at
        }
        for r in referrals[:10]
    ]

    last_joined_at = referrals[0].created_at if referrals else None

    return {
        "campaign_id": campaign_id,
        "referral_code": ref_code,
        "exists": True,
        "owner_email": owner.email,
        "owner_name": owner.first_name,
        "total_referrals": len(referrals),
        "recent_referrals": recent_referrals,
        "last_joined_at": last_joined_at
    }