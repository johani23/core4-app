# ====================================================================
# 💚 Core4.AI – Campaign Growth Service (FINAL CLEAN)
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
# NEXT UNLOCK
# =====================================================

def get_next_unlock(db: Session, campaign_id: int, buyers_joined: int):
    brackets = db.query(DiscountBracket).filter(
        DiscountBracket.campaign_id == campaign_id
    ).order_by(
        DiscountBracket.required_commitments.asc()
    ).all()

    for bracket in brackets:
        if buyers_joined < bracket.required_commitments:
            buyers_needed = bracket.required_commitments - buyers_joined
            return bracket.price, buyers_needed

    return None, 0


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