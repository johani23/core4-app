# ============================================================================
# 💚 Core4.AI – Campaign Router (FINAL PRODUCTION READY)
# ============================================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from db import get_db

from models.campaign import Campaign
from commitment.models import MarketCommitment as Commitment

from utils.referral import generate_referral_code

from services.campaign_growth import (
    count_buyers_joined,
    compute_pricing_state
)

router = APIRouter(
    prefix="/api/campaign",
    tags=["campaign"]
)


# =====================================================
# JOIN CAMPAIGN (FINAL)
# =====================================================
@router.post("/{campaign_id}/join")
def join_campaign(campaign_id: int, payload: dict, db: Session = Depends(get_db)):

    # -------------------------------------------------
    # Validate campaign
    # -------------------------------------------------
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id
    ).first()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # -------------------------------------------------
    # Extract + normalize payload
    # -------------------------------------------------
    email = payload.get("email", "").lower().strip()
    first_name = payload.get("first_name")
    city = payload.get("city")
    referred_by = payload.get("referred_by")

    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    # -------------------------------------------------
    # Prevent duplicate joins
    # -------------------------------------------------
    existing = db.query(Commitment).filter(
        Commitment.campaign_id == campaign_id,
        Commitment.email == email,
        Commitment.is_active == True
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="User already joined this campaign"
        )

    # -------------------------------------------------
    # Lock price at join time (CRITICAL)
    # -------------------------------------------------
    effective_price = campaign.current_price

    # -------------------------------------------------
    # Generate referral code (unique)
    # -------------------------------------------------
    referral_code = generate_referral_code(campaign_id, email)

    # -------------------------------------------------
    # Create commitment
    # -------------------------------------------------
    commitment = Commitment(
        campaign_id=campaign_id,
        email=email,
        commitment_price=effective_price,  # 🔥 critical for pricing integrity
        first_name=first_name,
        city=city,
        referred_by=referred_by,
        referral_code=referral_code,
        is_active=True
    )

    try:
        db.add(commitment)
        db.commit()
        db.refresh(commitment)

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Join failed (duplicate or conflict)")

    # -------------------------------------------------
    # 🔥 RECOMPUTE GROWTH STATE
    # -------------------------------------------------
    buyers = count_buyers_joined(db, campaign_id)

    pricing = compute_pricing_state(
        db,
        campaign_id,
        buyers
    )

    # -------------------------------------------------
    # OPTIONAL: sync campaign price safely
    # -------------------------------------------------
    try:
        if pricing["current_price"] is not None:
            campaign.current_price = pricing["current_price"]
            db.commit()
    except Exception:
        db.rollback()

    # -------------------------------------------------
    # RESPONSE
    # -------------------------------------------------
    return {
        "success": True,
        "buyers_joined": buyers,
        "referral_code": referral_code,

        # 🔥 PRICING ENGINE OUTPUT
        "current_price": pricing["current_price"],
        "next_unlock_price": pricing["next_price"],
        "buyers_needed_for_next_unlock": pricing["buyers_needed"]
    }