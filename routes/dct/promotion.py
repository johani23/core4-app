# ============================================================================
# 🔵 Core4.AI – DCT Promotion Activation
# Triggered after DCT confirmation
# ============================================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from db import get_db
from models.market_intention import MarketIntention
from models.dct_requirement import DCTRequirement

router = APIRouter(
    prefix="/dct/promotion",
    tags=["dct-promotion"]
)


@router.post("/{market_intention_id}/activate")
def activate_promotion(market_intention_id: int, db: Session = Depends(get_db)):

    # 1️⃣ Load DCT Requirement
    dct = db.query(DCTRequirement).filter(
        DCTRequirement.market_intention_id == market_intention_id
    ).first()

    if not dct:
        return {"error": "DCT requirement not found"}

    if dct.status != "confirmed":
        return {"error": "DCT must be confirmed before activation"}

    # 2️⃣ Load Market Intention
    mi = db.query(MarketIntention).filter(
        MarketIntention.id == market_intention_id
    ).first()

    if not mi:
        return {"error": "Market intention not found"}

    # 3️⃣ Activate
    dct.status = "active"
    dct.updated_at = datetime.utcnow()

    mi.dct_status = "active"
    mi.status = "executing"

    db.commit()

    return {
        "status": "promotion_activated",
        "market_intention_id": market_intention_id
    }
