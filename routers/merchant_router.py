# ====================================================================
# 💚 Core4.AI – Merchant Router (FINAL CLEAN)
# ====================================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from db import get_db
from models.market_request import MarketRequest
from models.campaign import Campaign
from commitment.models import MarketCommitment as Commitment


router = APIRouter(
    prefix="/api/merchant",
    tags=["merchant-activation"]
)


# =====================================================
# HOT DEMAND (PRE-CAMPAIGN)
# =====================================================

@router.get("/opportunities")
def get_opportunities(db: Session = Depends(get_db)):
    requests = db.query(
        MarketRequest.query,
        func.count(MarketRequest.id).label("count")
    ).filter(
        MarketRequest.campaign_id.is_(None)
    ).group_by(
        MarketRequest.query
    ).order_by(
        func.count(MarketRequest.id).desc()
    ).limit(10).all()

    return [
        {
            "query": r.query,
            "demand_count": r.count
        }
        for r in requests
    ]


# =====================================================
# ACTIVE CAMPAIGNS (READY TO BID)
# =====================================================

@router.get("/campaigns")
def merchant_campaigns(db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()

    result = []

    for c in campaigns:
        buyers = db.query(Commitment).filter(
            Commitment.campaign_id == c.id
        ).count()

        result.append({
            "id": c.id,
            "title": c.title,
            "current_price": c.current_price,
            "retail_price": c.retail_price,
            "demand": buyers,
            "target": c.target_buyers,
            "status": c.status
        })

    return result


# =====================================================
# SUBMIT BETTER OFFER
# =====================================================

@router.post("/offer")
def submit_offer(payload: dict, db: Session = Depends(get_db)):
    campaign_id = payload.get("campaign_id")
    new_price = payload.get("price")

    if campaign_id is None:
        raise HTTPException(status_code=400, detail="campaign_id is required")

    if new_price is None:
        raise HTTPException(status_code=400, detail="price is required")

    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id
    ).first()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if float(new_price) >= float(campaign.current_price):
        raise HTTPException(
            status_code=400,
            detail="price must be lower than current_price"
        )

    campaign.current_price = float(new_price)
    db.commit()
    db.refresh(campaign)

    return {
        "success": True,
        "campaign_id": campaign.id,
        "new_price": campaign.current_price
    }