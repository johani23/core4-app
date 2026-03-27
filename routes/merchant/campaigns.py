# ============================================================================
# 💚 Core4.AI – Merchant Campaigns API (DEBUG VERSION)
# ============================================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from models.campaign import Campaign
from models.product import Product
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid

router = APIRouter(
    prefix="/api/merchant/campaigns",
    tags=["merchant-campaigns"]
)

# ============================================================================
# SCHEMA
# ============================================================================
class CampaignCreate(BaseModel):
    product_id: Optional[int] = None
    intention_id: Optional[int] = None
    channel: str
    context_note: Optional[str] = None


# ============================================================================
# GET ALL
# ============================================================================
@router.get("/")
def get_campaigns(db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()

    return [
        {
            "id": c.id,
            "product_id": c.product_id,
            "intention_id": c.intention_id,
            "channel": c.channel,
            "status": c.status,
            "created_at": c.created_at,
        }
        for c in campaigns
    ]


# ============================================================================
# GET ONE
# ============================================================================
@router.get("/{campaign_id}")
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    product = None
    if campaign.product_id:
        product = db.query(Product).filter(Product.id == campaign.product_id).first()

    return {
        "id": campaign.id,
        "status": campaign.status,
        "created_at": campaign.created_at,
        "channel": campaign.channel,
        "context_note": campaign.context_note,
        "product": product and {
            "id": product.id,
            "name": product.name,
            "category": product.category,
        },
    }


# ============================================================================
# CREATE (DEBUG)
# ============================================================================
@router.post("/")
def create_campaign(payload: CampaignCreate, db: Session = Depends(get_db)):

    print("🚀 DEBUG ROUTE HIT")   # 🔥 FIRST DEBUG

    if not payload.product_id and not payload.intention_id:
        raise HTTPException(
            status_code=400,
            detail="يجب اختيار منتج أو نية سوق لإنشاء حملة"
        )

    product = None

    if payload.product_id:
        product = db.query(Product).filter(Product.id == payload.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="المنتج غير موجود")

    # 🔥 DEBUG VALUES
    title_value = product.name if product else "Auto Campaign"
    slug_value = str(uuid.uuid4())[:8]

    print("🚀 SLUG:", slug_value, "TITLE:", title_value)   # 🔥 SECOND DEBUG

    campaign = Campaign(
        product_id=payload.product_id,
        intention_id=payload.intention_id,
        channel=payload.channel,
        context_note=payload.context_note,

        title=title_value,
        slug=slug_value,

        retail_price=product.price if product else 0,
        current_price=product.price if product else 0,
        target_buyers=100,

        status="نشطة",
        created_at=datetime.utcnow(),
    )

    db.add(campaign)
    db.commit()
    db.refresh(campaign)

    return {
        "status": "created",
        "id": campaign.id,
    }