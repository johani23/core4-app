# ====================================================================
# 💚 Core4.AI – Campaign Join Router (FINAL + GROWTH TRACKING)
# ====================================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_db
from models.campaign import Campaign
from models.commitment import Commitment
from utils.referral import generate_referral_code

from services.campaign_growth import (
    count_buyers_joined,
    get_next_unlock,
    get_recent_counts,
    get_recent_joins,
    referral_stats
)

# 🚀 Growth
from services.growth_logger import log_event

router = APIRouter(
    prefix="/api/campaign",
    tags=["campaign"]
)


# ====================================================================
# JOIN CAMPAIGN
# ====================================================================

@router.post("/{campaign_id}/join")
def join_campaign(
    campaign_id: int,
    payload: dict,
    db: Session = Depends(get_db)
):

    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id
    ).first()

    if not campaign:
        raise HTTPException(
            status_code=404,
            detail="Campaign not found"
        )

    commitment = Commitment(
        campaign_id=campaign_id,
        email=payload["email"].lower(),
        commitment_price=payload["commitment_price"],
        first_name=payload.get("first_name"),
        city=payload.get("city"),
        referral_source=payload.get("referral_source")
    )

    db.add(commitment)
    db.commit()
    db.refresh(commitment)

    # 🚀 Growth Event (JOIN)
    log_event(
        db=db,
        event_type="campaign_joined",
        user_id=None,
        metadata={
            "campaign_id": campaign_id
        }
    )

    # 🚀 Referral Event (if used)
    if payload.get("referral_source"):
        log_event(
            db=db,
            event_type="referral_used",
            user_id=None,
            metadata={
                "campaign_id": campaign_id,
                "source": payload.get("referral_source")
            }
        )

    buyers_joined = count_buyers_joined(
        db,
        campaign_id
    )

    next_price, buyers_needed = get_next_unlock(
        db,
        campaign_id,
        buyers_joined
    )

    ref_code = generate_referral_code(
        campaign_id,
        payload["email"]
    )

    return {
        "success": True,
        "buyers_joined": buyers_joined,
        "referral_code": ref_code,
        "next_unlock_price": next_price,
        "buyers_needed_for_next_unlock": buyers_needed
    }


# ====================================================================
# RECENT JOINS
# ====================================================================

@router.get("/{campaign_id}/recent-joins")
def recent_joins(campaign_id: int, db: Session = Depends(get_db)):

    joins = get_recent_joins(db, campaign_id)
    today, hour = get_recent_counts(db, campaign_id)

    return {
        "buyers_joined_today": today,
        "buyers_joined_last_hour": hour,
        "items": [
            {
                "name": j.first_name or "Someone",
                "city": j.city,
                "joined_at": j.timestamp
            }
            for j in joins
        ]
    }


# ====================================================================
# REFERRALS
# ====================================================================

@router.get("/{campaign_id}/referrals/{ref_code}")
def get_referrals(campaign_id: int, ref_code: str, db: Session = Depends(get_db)):

    return referral_stats(db, campaign_id, ref_code)