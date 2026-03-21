# ====================================================================
# 💚 Core4.AI – Campaign Router (PRODUCTION SAFE + OPTIMIZED)
# ====================================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
import re

from db import get_db

from models.campaign import Campaign
from commitment.models import MarketCommitment as Commitment
from models.discount_bracket import DiscountBracket
from models.market_request import MarketRequest
from models.merchant_offer import MerchantOffer

from utils.referral import generate_referral_code

from services.campaign_growth import (
    count_buyers_joined,
    get_next_unlock,
    get_recent_counts,
    get_recent_joins,
    referral_stats
)

# 🚀 Growth (ONLY for write operations)
from services.growth_logger import log_event

router = APIRouter(
    prefix="/api/campaign",
    tags=["campaign"]
)

# ====================================================================
# HELPERS
# ====================================================================

def generate_slug(text: str):
    return re.sub(r'[^a-zA-Z0-9]+', '-', text.lower()).strip('-')


# ====================================================================
# LIST CAMPAIGNS (🔥 FIXED)
# ====================================================================

@router.get("/")
def list_campaigns(db: Session = Depends(get_db)):

    campaigns = db.query(Campaign).order_by(
        Campaign.created_at.desc()
    ).limit(20).all()  # ✅ LIMIT

    campaign_ids = [c.id for c in campaigns]

    buyers_map = {}

    if campaign_ids:
        rows = db.query(
            Commitment.campaign_id,
            func.count(Commitment.id)
        ).filter(
            Commitment.campaign_id.in_(campaign_ids)
        ).group_by(
            Commitment.campaign_id
        ).all()

        buyers_map = {
            campaign_id: count
            for campaign_id, count in rows
        }

    return [
        {
            "id": c.id,
            "slug": c.slug,
            "title": c.title,
            "current_price": c.current_price,
            "target_buyers": c.target_buyers,
            "buyers": buyers_map.get(c.id, 0),
            "status": c.status
        }
        for c in campaigns
    ]


# ====================================================================
# CREATE CAMPAIGN
# ====================================================================

@router.post("/create")
def create_campaign(payload: dict, db: Session = Depends(get_db)):
    try:
        campaign = Campaign(
            slug=generate_slug(payload["title"]),
            title=payload["title"],
            retail_price=payload.get("retail_price", 0),
            current_price=payload.get("current_price", 0),
            target_buyers=payload.get("target_buyers", 100),
            channel=payload.get("channel", "organic"),
            status="نشطة"
        )

        db.add(campaign)
        db.commit()
        db.refresh(campaign)

        return {
            "success": True,
            "campaign_id": campaign.id,
            "slug": campaign.slug
        }

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Campaign with this slug already exists"
        )


# ====================================================================
# GET CAMPAIGN (🔥 FIXED)
# ====================================================================

@router.get("/{campaign_id}")
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):

    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id
    ).first()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # ❌ REMOVED log_event here (blocking)

    brackets = db.query(DiscountBracket).filter(
        DiscountBracket.campaign_id == campaign_id
    ).order_by(
        DiscountBracket.required_commitments
    ).all()

    buyers_joined = db.query(func.count(Commitment.id)).filter(
        Commitment.campaign_id == campaign_id
    ).scalar()

    waiting_count = db.query(func.count(MarketRequest.id)).filter(
        MarketRequest.campaign_id == campaign_id
    ).scalar()

    offers = db.query(MerchantOffer).filter(
        MerchantOffer.campaign_id == campaign_id,
        MerchantOffer.is_active == True
    ).all()

    best_offer = min(offers, key=lambda o: o.current_price) if offers else None

    base_price = (
        min([o.base_price for o in offers])
        if offers else campaign.retail_price or campaign.current_price or 0
    )

    current_price = (
        best_offer.current_price if best_offer else campaign.current_price
    )

    return {
        "campaign": {
            "id": campaign.id,
            "slug": campaign.slug,
            "title": campaign.title,
            "retail_price": campaign.retail_price,
            "current_price": current_price
        },
        "buyers_joined": buyers_joined,
        "waiting_count": waiting_count,
        "discount_brackets": [
            {
                "id": b.id,
                "name": b.name,
                "required_commitments": b.required_commitments,
                "discount_percent": b.discount_percent,
                "price": b.price,
                "rank": b.rank,
            }
            for b in brackets
        ],
        "base_price": base_price,
        "best_offer_price": current_price,
        "best_offer": (
            {
                "id": best_offer.id,
                "merchant_id": best_offer.merchant_id,
                "base_price": best_offer.base_price,
                "current_price": best_offer.current_price
            }
            if best_offer else None
        )
    }


# ====================================================================
# JOIN CAMPAIGN (🔥 KEEP GROWTH HERE)
# ====================================================================

@router.post("/{campaign_id}/join")
def join_campaign(campaign_id: int, payload: dict, db: Session = Depends(get_db)):

    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id
    ).first()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    email = (payload.get("email") or "").lower().strip()

    if not email:
        raise HTTPException(status_code=400, detail="email is required")

    existing = db.query(Commitment).filter(
        Commitment.campaign_id == campaign_id,
        Commitment.email == email
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Already joined")

    ref_code = generate_referral_code(campaign_id, email)

    commitment = Commitment(
        campaign_id=campaign_id,
        email=email,
        commitment_price=payload.get(
            "commitment_price",
            campaign.current_price
        ),
        first_name=payload.get("first_name"),
        city=payload.get("city"),
        referral_code=ref_code,
        referred_by=payload.get("ref_code")
    )

    db.add(commitment)
    db.commit()
    db.refresh(commitment)

    # 🚀 SAFE: logging only on write
    log_event(
        db=db,
        event_type="campaign_joined",
        user_id=None,
        metadata={
            "campaign_id": campaign_id,
            "ref_code_used": payload.get("ref_code")
        }
    )

    buyers_joined = count_buyers_joined(db, campaign_id)

    offers = db.query(MerchantOffer).filter(
        MerchantOffer.campaign_id == campaign_id,
        MerchantOffer.is_active == True
    ).all()

    best_offer = min(offers, key=lambda o: o.current_price) if offers else None

    current_price = (
        best_offer.current_price if best_offer else campaign.current_price
    )

    next_price, buyers_needed = get_next_unlock(
        db,
        campaign_id,
        buyers_joined
    )

    return {
        "success": True,
        "buyers": buyers_joined,
        "current_price": current_price,
        "referral_code": ref_code,
        "next_unlock_price": next_price,
        "buyers_needed": buyers_needed
    }