# ====================================================================
# 💚 Core4.AI – Campaign Router (FINAL PRODUCTION SAFE)
# ====================================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from db import get_db

from models.campaign import Campaign
from commitment.models import MarketCommitment as Commitment

from utils.referral import generate_referral_code

from services.campaign_growth import count_buyers_joined
from services.campaign_pricing import compute_pricing_state

from services.growth_logger import log_event

router = APIRouter(prefix="/api/campaign", tags=["campaign"])


# =========================================================
# HELPERS
# =========================================================
def _get_campaign_or_404(db: Session, campaign_id: int):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


# =====================================================
# LIST CAMPAIGNS (🔥 MUST COME FIRST)
# =====================================================
@router.get("/")
def list_campaigns(db: Session = Depends(get_db)):

    campaigns = db.query(Campaign).all()

    result = []

    for c in campaigns:
        buyers_joined = count_buyers_joined(db, c.id)
        pricing = compute_pricing_state(db, c.id, buyers_joined)

        buyers_needed = pricing.get("buyers_needed") or 0

        result.append({
            "id": c.id,
            "title": c.title,
            "retail_price": c.retail_price,
            "current_price": pricing.get("current_price"),
            "buyers_joined": buyers_joined,
            "final_target": c.target_buyers or 100,
         })

    return result# =========================================================
# GET CAMPAIGN
# =========================================================
@router.get("/{campaign_id}")
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):

    campaign = _get_campaign_or_404(db, campaign_id)

    buyers_joined = count_buyers_joined(db, campaign_id)

    pricing = compute_pricing_state(db, campaign_id, buyers_joined)

    return {
        "campaign": {
            "id": campaign.id,
            "title": campaign.title,
            "retail_price": campaign.retail_price,
            "current_price": pricing["current_price"],
            "target_buyers": campaign.target_buyers,
        },
        "buyers_joined": buyers_joined,
        "discount_brackets": pricing["brackets"],
        "next_unlock_price": pricing["next_price"],
        "buyers_needed": pricing["buyers_needed"],
    }


# =========================================================
# JOIN CAMPAIGN
# =========================================================
@router.post("/{campaign_id}/join")
def join_campaign(campaign_id: int, payload: dict, db: Session = Depends(get_db)):

    campaign = _get_campaign_or_404(db, campaign_id)

    email = (payload.get("email") or "").lower().strip()

    if not email:
        raise HTTPException(status_code=400, detail="email required")

    existing = db.query(Commitment).filter(
        Commitment.campaign_id == campaign_id,
        Commitment.email == email
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Already joined")

    buyers_joined = count_buyers_joined(db, campaign_id)
    pricing = compute_pricing_state(db, campaign_id, buyers_joined)

    ref_code = generate_referral_code(campaign_id, email)

    commitment = Commitment(
        campaign_id=campaign_id,
        email=email,
        commitment_price=pricing["current_price"],
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
            }
        )

        db.commit()

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Already joined")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    # 🔥 recompute AFTER commit
    buyers_joined = count_buyers_joined(db, campaign_id)
    pricing = compute_pricing_state(db, campaign_id, buyers_joined)

    return {
        "success": True,
        "buyers": buyers_joined,
        "referral_code": ref_code,
        "next_unlock_price": pricing["next_price"],
        "buyers_needed": pricing["buyers_needed"],
        "current_price": pricing["current_price"],
    }


# =========================================================
# RECENT JOINS
# =========================================================
@router.get("/{campaign_id}/recent-joins")
def get_recent_joins(campaign_id: int, db: Session = Depends(get_db)):

    joins = (
        db.query(Commitment)
        .filter(
            Commitment.campaign_id == campaign_id,
            Commitment.is_active == True
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
                "time_ago": "just now"
            }
            for j in joins
        ]
    }