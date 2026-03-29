# ============================================================================
# 💚 Core4.AI – Campaign Router (FINAL PRODUCTION SAFE)
# ============================================================================

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db import get_db
from models.campaign import Campaign
from models.discount_bracket import DiscountBracket
from commitment.models import MarketCommitment as Commitment

from services.campaign_growth import count_buyers_joined
from services.campaign_pricing import compute_pricing_state
from services.growth_logger import log_event
from utils.referral import generate_referral_code

router = APIRouter(prefix="/api/campaign", tags=["campaign"])


# =========================================================
# HELPERS
# =========================================================
def _get_campaign_or_404(db: Session, campaign_id: int):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


def _time_ago(value):
    if not value:
        return "recently"

    now = datetime.utcnow()
    diff = now - value

    if diff.total_seconds() < 60:
        return "just now"
    if diff.total_seconds() < 3600:
        mins = int(diff.total_seconds() // 60)
        return f"{mins} min ago"
    if diff.total_seconds() < 86400:
        hours = int(diff.total_seconds() // 3600)
        return f"{hours}h ago"

    days = diff.days
    return f"{days}d ago"


# =========================================================
# LIST CAMPAIGNS (MUST COME BEFORE /{campaign_id})
# =========================================================
@router.get("/")
def list_campaigns(db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).all()
    result = []

    for c in campaigns:
        buyers_joined = count_buyers_joined(db, c.id)
        pricing = compute_pricing_state(db, c.id, buyers_joined)

        final_target = int(getattr(c, "target_buyers", 0) or 100)
        buyers_needed = int(pricing.get("buyers_needed") or 0)

        next_unlock_threshold = (
            buyers_joined + buyers_needed if buyers_needed > 0 else final_target
        )

        result.append({
            "id": c.id,
            "title": c.title,
            "retail_price": float(getattr(c, "retail_price", 0) or 0),
            "current_price": float(pricing.get("current_price") or getattr(c, "retail_price", 0) or 0),
            "buyers_joined": buyers_joined,
            "final_target": final_target,
            "next_unlock_threshold": next_unlock_threshold,
        })

    return result


# =========================================================
# GET CAMPAIGN
# =========================================================
@router.get("/{campaign_id}")
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    campaign = _get_campaign_or_404(db, campaign_id)

    buyers_joined = count_buyers_joined(db, campaign_id)
    pricing = compute_pricing_state(db, campaign_id, buyers_joined)

    target_buyers = int(getattr(campaign, "target_buyers", 0) or 100)

    return {
        "campaign": {
            "id": campaign.id,
            "title": campaign.title,
            "retail_price": float(getattr(campaign, "retail_price", 0) or 0),
            "current_price": float(pricing.get("current_price") or getattr(campaign, "retail_price", 0) or 0),
            "target_buyers": target_buyers,
        },
        "buyers_joined": buyers_joined,
        "discount_brackets": pricing.get("brackets") or [],
        "next_unlock_price": pricing.get("next_price"),
        "buyers_needed": int(pricing.get("buyers_needed") or 0),
    }


# =========================================================
# JOIN CAMPAIGN
# =========================================================
@router.post("/{campaign_id}/join")
def join_campaign(campaign_id: int, payload: dict, db: Session = Depends(get_db)):
    _get_campaign_or_404(db, campaign_id)

    email = (payload.get("email") or "").strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="email required")

    existing = (
        db.query(Commitment)
        .filter(
            Commitment.campaign_id == campaign_id,
            Commitment.email == email,
        )
        .first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="Already joined")

    buyers_joined_before = count_buyers_joined(db, campaign_id)
    pricing_before = compute_pricing_state(db, campaign_id, buyers_joined_before)

    ref_code = generate_referral_code(campaign_id, email)

    commitment = Commitment(
        campaign_id=campaign_id,
        email=email,
        commitment_price=float(pricing_before.get("current_price") or 0),
        first_name=payload.get("first_name"),
        city=payload.get("city"),
        referral_code=ref_code,
        referred_by=payload.get("ref_code"),
        is_active=True,
    )

    try:
        db.add(commitment)

        log_event(
            db=db,
            event_type="campaign_joined",
            user_id=None,
            metadata={
                "campaign_id": campaign_id,
                "ref_code_used": payload.get("ref_code"),
            },
        )

        db.commit()

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Already joined")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    buyers_joined_after = count_buyers_joined(db, campaign_id)
    pricing_after = compute_pricing_state(db, campaign_id, buyers_joined_after)

    return {
        "success": True,
        "buyers": buyers_joined_after,
        "referral_code": ref_code,
        "next_unlock_price": pricing_after.get("next_price"),
        "buyers_needed": int(pricing_after.get("buyers_needed") or 0),
        "current_price": float(pricing_after.get("current_price") or 0),
    }


# =========================================================
# RECENT JOINS
# =========================================================
@router.get("/{campaign_id}/recent-joins")
def get_recent_joins(campaign_id: int, db: Session = Depends(get_db)):
    _get_campaign_or_404(db, campaign_id)

    joins = (
        db.query(Commitment)
        .filter(
            Commitment.campaign_id == campaign_id,
            Commitment.is_active == True,
        )
        .order_by(Commitment.created_at.desc())
        .limit(10)
        .all()
    )

    return {
        "joins": [
            {
                "id": j.id,
                "email": j.email,
                "first_name": j.first_name,
                "time_ago": _time_ago(getattr(j, "created_at", None)),
            }
            for j in joins
        ]
    }


# =========================================================
# REFERRAL STATS
# =========================================================
@router.get("/{campaign_id}/referrals/{ref_code}")
def referral_stats(campaign_id: int, ref_code: str, db: Session = Depends(get_db)):
    _get_campaign_or_404(db, campaign_id)

    converted_invites = (
        db.query(Commitment)
        .filter(
            Commitment.campaign_id == campaign_id,
            Commitment.referred_by == ref_code,
            Commitment.is_active == True,
        )
        .count()
    )

    return {
        "campaign_id": campaign_id,
        "ref_code": ref_code,
        "converted_invites": converted_invites,
    }


# =========================================================
# MOMENTUM
# =========================================================
@router.get("/{campaign_id}/momentum")
def campaign_momentum(campaign_id: int, db: Session = Depends(get_db)):
    campaign = _get_campaign_or_404(db, campaign_id)

    now = datetime.utcnow()
    day_ago = now - timedelta(days=1)
    hour_ago = now - timedelta(hours=1)

    buyers_joined = count_buyers_joined(db, campaign_id)
    target_buyers = int(getattr(campaign, "target_buyers", 0) or 100)

    recent_joins_24h = (
        db.query(Commitment)
        .filter(
            Commitment.campaign_id == campaign_id,
            Commitment.is_active == True,
            Commitment.created_at >= day_ago,
        )
        .count()
    )

    recent_joins_1h = (
        db.query(Commitment)
        .filter(
            Commitment.campaign_id == campaign_id,
            Commitment.is_active == True,
            Commitment.created_at >= hour_ago,
        )
        .count()
    )

    progress_ratio = buyers_joined / target_buyers if target_buyers else 0

    is_near_unlock = progress_ratio >= 0.8
    is_trending = recent_joins_24h >= 2 or recent_joins_1h >= 1

    return {
        "campaign_id": campaign_id,
        "buyers_joined": buyers_joined,
        "recent_joins_24h": recent_joins_24h,
        "recent_joins_1h": recent_joins_1h,
        "is_near_unlock": is_near_unlock,
        "is_trending": is_trending,
    }

# =========================================================
# CREATE BRACKETS (ADMIN / SETUP)
# =========================================================
@router.post("/{campaign_id}/brackets")
def create_brackets(campaign_id: int, db: Session = Depends(get_db)):

    _get_campaign_or_404(db, campaign_id)

    brackets = [
        (5, 4800),
        (10, 4600),
        (20, 4300),
        (50, 4000),
    ]

    for required, price in brackets:
        db.add(DiscountBracket(
            campaign_id=campaign_id,
            required_commitments=required,
            price=price
        ))

    db.commit()

    return {"success": True, "message": "Brackets created"}