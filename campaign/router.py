# ============================================================================
# 💚 Core4.AI – Campaign Router (PRODUCTION SAFE + FRONTEND ALIGNED)
# ============================================================================

from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_db
from models.merchant_offer import MerchantOffer
from commitment.models import Commitment
from commitment.service import compute_engine_state, upsert_commitment
from campaign.momentum import compute_campaign_momentum


router = APIRouter(
    prefix="/api/campaign",
    tags=["campaign"]
)


# ============================================================================
# Schema
# ============================================================================

class JoinCampaignPayload(BaseModel):
    email: EmailStr
    first_name: str | None = None
    city: str | None = None
    referral_source: str | None = None


# ============================================================================
# Helpers
# ============================================================================

def _calculate_unlock_price(base_price: float, discount_percent: float | None):
    if discount_percent is None:
        return base_price
    return round(base_price * (1 - discount_percent / 100), 2)


# ============================================================================
# LIST CAMPAIGNS
# Put "/" BEFORE "/{offer_id}" to avoid route conflicts
# ============================================================================

@router.get("/")
def list_campaigns(db: Session = Depends(get_db)):

    offers = db.query(MerchantOffer).filter(
        MerchantOffer.is_active == True
    ).all()

    campaigns = []

    for offer in offers:
        state = compute_engine_state(db, offer.id)

        commitments_count = state["commitments_count"]
        brackets = state["brackets"]
        current_price = state["current_price"]

        next_unlock = None
        for b in brackets:
            if not b["unlocked"]:
                next_unlock = b["required_commitments"]
                break

        final_target = brackets[-1]["required_commitments"] if brackets else 0

        progress = 0
        if final_target > 0:
            progress = round((commitments_count / final_target) * 100)

        if commitments_count == 0:
            status = "جديدة"
        elif commitments_count < 10:
            status = "تجريبية"
        elif commitments_count < 50:
            status = "نشطة"
        else:
            status = "🔥 قوية"

        campaigns.append({
            "id": offer.id,
            "title": offer.title,
            "status": status,
            "buyers": commitments_count,
            "next_unlock": next_unlock,
            "current_price": current_price,
            "progress": progress
        })

    campaigns.sort(key=lambda x: x["buyers"], reverse=True)
    return campaigns


# ============================================================================
# GET SINGLE CAMPAIGN
# ============================================================================

@router.get("/{offer_id}")
def get_campaign(offer_id: int, db: Session = Depends(get_db)):

    offer = db.query(MerchantOffer).filter(
        MerchantOffer.id == offer_id,
        MerchantOffer.is_active == True
    ).first()

    if not offer:
        raise HTTPException(status_code=404, detail="Campaign not found")

    state = compute_engine_state(db, offer_id)

    commitments_count = state["commitments_count"]
    brackets = state["brackets"]
    active_bracket = state["active_bracket"]
    current_price = state["current_price"]

    next_unlock = None
    next_unlock_price = None

    for b in brackets:
        if not b["unlocked"]:
            next_unlock = b["required_commitments"]
            next_unlock_price = _calculate_unlock_price(
                offer.base_price,
                b["discount_percent"]
            )
            break

    max_target = brackets[-1]["required_commitments"] if brackets else 0

    progress = 0
    if max_target > 0:
        progress = round((commitments_count / max_target) * 100, 2)

    buyers_needed = max(next_unlock - commitments_count, 0) if next_unlock else 0

    return {
        "campaign": {
            "id": offer.id,
            "title": offer.title,
            "base_price": offer.base_price,
            "retail_price": offer.base_price,
            "currency": offer.currency
        },
        "market": {
            "buyers_joined": commitments_count,
            "current_price": current_price,
            "progress_percent": progress,
            "next_unlock": next_unlock,
            "next_unlock_price": next_unlock_price,
            "buyers_needed": buyers_needed
        },
        "active_bracket": active_bracket,
        "price_ladder": brackets
    }


# ============================================================================
# JOIN CAMPAIGN
# ============================================================================

@router.post("/{offer_id}/join")
def join_campaign(
    offer_id: int,
    payload: JoinCampaignPayload,
    db: Session = Depends(get_db)
):

    offer = db.query(MerchantOffer).filter(
        MerchantOffer.id == offer_id,
        MerchantOffer.is_active == True
    ).first()

    if not offer:
        raise HTTPException(status_code=404, detail="Campaign not found")

    email = payload.email.lower().strip()

    existing = db.query(Commitment).filter(
        Commitment.offer_id == offer_id,
        Commitment.buyer_id == email,
    ).first()

    if existing and existing.is_active:
        return {
            "status": "already_joined",
            "offer_id": offer_id,
            "commitment_id": existing.id
        }

    commitment = upsert_commitment(
        db=db,
        offer_id=offer_id,
        buyer_id=email,
        quantity=1,
        commitment_type="buyer"
    )

    return {
        "status": "joined",
        "offer_id": offer_id,
        "commitment_id": commitment.id
    }


# ============================================================================
# MOMENTUM
# ============================================================================

@router.get("/{offer_id}/momentum")
def get_campaign_momentum(
    offer_id: int,
    db: Session = Depends(get_db)
):
    offer = db.query(MerchantOffer).filter(
        MerchantOffer.id == offer_id,
        MerchantOffer.is_active == True
    ).first()

    if not offer:
        raise HTTPException(status_code=404, detail="Campaign not found")

    momentum = compute_campaign_momentum(db, offer_id)

    return {
        "campaign_id": offer_id,
        "momentum": momentum
    }


# ============================================================================
# RECENT JOINS
# ============================================================================

@router.get("/{offer_id}/recent-joins")
def get_recent_joins(
    offer_id: int,
    db: Session = Depends(get_db)
):

    offer = db.query(MerchantOffer).filter(
        MerchantOffer.id == offer_id,
        MerchantOffer.is_active == True
    ).first()

    if not offer:
        raise HTTPException(status_code=404, detail="Campaign not found")

    rows = (
        db.query(Commitment)
        .filter(
            Commitment.offer_id == offer_id,
            Commitment.is_active == True
        )
        .order_by(Commitment.created_at.desc())
        .limit(8)
        .all()
    )

    items = []

    for row in rows:
        raw_buyer = getattr(row, "buyer_id", "buyer")
        safe_name = raw_buyer.split("@")[0] if "@" in raw_buyer else raw_buyer
        safe_name = safe_name[:1].upper() + safe_name[1:] if safe_name else "Buyer"

        items.append({
            "name": safe_name,
            "city": None,
            "created_at": row.created_at.isoformat() if row.created_at else None
        })

    return {
        "items": items
    }