# ====================================================================
# 💚 Core4.AI – Campaign Router (FINAL ACTIVATION READY)
# ====================================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


from datetime import datetime, timedelta, timezone

from db import get_db

from models.campaign import Campaign
from commitment.models import MarketCommitment as Commitment


from utils.referral import generate_referral_code
from services.campaign_growth import count_buyers_joined, get_next_unlock
from services.growth_logger import log_event

from schemas.campaign_growth import (
    JoinCampaignIn,
    JoinCampaignOut,
    RecentJoinItem,
    RecentJoinsOut,
    ReferralStatsOut,
)

router = APIRouter(prefix="/api/campaign", tags=["campaign"])



# ====================================================================
# HELPERS
# ====================================================================

def _get_campaign_or_404(db: Session, campaign_id: int) -> Campaign:
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


def _buyers_joined_in_last_hours(db: Session, campaign_id: int, hours: int) -> int:
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    return (
        db.query(Commitment)
        .filter(
            Commitment.campaign_id == campaign_id,
            Commitment.is_active == True,
            Commitment.created_at >= since,
        )
        .count()
    )


def _buyers_joined_today(db: Session, campaign_id: int) -> int:
    now = datetime.now(timezone.utc)
    start_of_day = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    return (
        db.query(Commitment)
        .filter(
            Commitment.campaign_id == campaign_id,
            Commitment.is_active == True,
            Commitment.created_at >= start_of_day,
        )
        .count()
    )


# ====================================================================
# JOIN CAMPAIGN
# ====================================================================

@router.post("/{campaign_id}/join", response_model=JoinCampaignOut)
def join_campaign(
    campaign_id: int,
    payload: JoinCampaignIn,
    db: Session = Depends(get_db),
):
    campaign = _get_campaign_or_404(db, campaign_id)

    email = payload.email.lower().strip()

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

    # -------------------------------------------------
    # Backend owns price selection
    # -------------------------------------------------
    effective_price = campaign.current_price

    ref_code = generate_referral_code(campaign_id, email)

    commitment = Commitment(
        campaign_id=campaign_id,
        email=email,
        commitment_price=effective_price,
        first_name=payload.first_name,
        city=payload.city,
        referral_code=ref_code,
        referred_by=payload.ref_code,
        is_active=True,
    )

    try:
        db.add(commitment)

        log_event(
            db=db,
            event_type="campaign_joined",
            user_id=None,
            campaign_id=campaign_id,
            ref_code=payload.ref_code,
            metadata={
                "email": email,
                "generated_referral_code": ref_code,
            },
        )

        db.commit()
        db.refresh(commitment)

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Already joined")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"join failed: {str(e)}")

    buyers_joined = count_buyers_joined(db, campaign_id)
    next_price, buyers_needed = get_next_unlock(db, campaign_id, buyers_joined)

    return JoinCampaignOut(
        success=True,
        buyers_joined=buyers_joined,
        referral_code=ref_code,
        next_unlock_price=next_price,
        buyers_needed_for_next_unlock=buyers_needed,
    )


# ====================================================================
# RECENT JOINS
# ====================================================================

@router.get("/{campaign_id}/recent-joins", response_model=RecentJoinsOut)
def recent_joins(campaign_id: int, db: Session = Depends(get_db)):
    _get_campaign_or_404(db, campaign_id)

    rows = (
        db.query(Commitment)
        .filter(
            Commitment.campaign_id == campaign_id,
            Commitment.is_active == True,
        )
        .order_by(Commitment.created_at.desc())
        .limit(10)
        .all()
    )

    items = [
        RecentJoinItem(
            first_name=getattr(row, "first_name", None),
            city=getattr(row, "city", None),
            joined_at=row.created_at,
        )
        for row in rows
    ]

    return RecentJoinsOut(
        buyers_joined_today=_buyers_joined_today(db, campaign_id),
        buyers_joined_last_hour=_buyers_joined_in_last_hours(db, campaign_id, 1),
        items=items,
    )


# ====================================================================
# REFERRAL STATS
# ====================================================================

@router.get("/{campaign_id}/referrals/{ref_code}", response_model=ReferralStatsOut)
def referral_stats(campaign_id: int, ref_code: str, db: Session = Depends(get_db)):
    _get_campaign_or_404(db, campaign_id)

    friends_joined = (
        db.query(Commitment)
        .filter(
            Commitment.campaign_id == campaign_id,
            Commitment.referred_by == ref_code,
            Commitment.is_active == True,
        )
        .count()
    )

    invite_link = f"/campaign/{campaign_id}?ref={ref_code}"

    return ReferralStatsOut(
        ref_code=ref_code,
        invite_link=invite_link,
        friends_joined=friends_joined,
    )


# ====================================================================
# MOMENTUM
# ====================================================================

from schemas.campaign_growth import CampaignMomentumOut

@router.get("/{campaign_id}/momentum", response_model=CampaignMomentumOut)
def campaign_momentum(campaign_id: int, db: Session = Depends(get_db)):
    campaign = _get_campaign_or_404(db, campaign_id)

    buyers_joined = count_buyers_joined(db, campaign_id)
    next_price, buyers_needed = get_next_unlock(db, campaign_id, buyers_joined)

    recent_24h = _buyers_joined_in_last_hours(db, campaign_id, 24)
    recent_1h = _buyers_joined_in_last_hours(db, campaign_id, 1)

    is_near_unlock = buyers_needed is not None and buyers_needed <= 3
    is_trending = recent_24h >= 5 or recent_1h >= 2

    return CampaignMomentumOut(
        campaign_id=campaign.id,
        buyers_joined=buyers_joined,
        recent_joins_24h=recent_24h,
        buyers_needed_for_next_unlock=buyers_needed,
        next_unlock_price=next_price,
        is_trending=is_trending,
        is_near_unlock=is_near_unlock,
    )