from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db

from models.market_intention import MarketIntention
from models.merchant_commitment import MerchantCommitment

router = APIRouter(
    prefix="/merchant/commit",
    tags=["merchant-commitment"]
)


@router.post("/{market_intention_id}")
def create_commitment(market_intention_id: int, payload: dict, db: Session = Depends(get_db)):
    """
    payload:
    {
        "merchant_id": 1,
        "capacity": 500,
        "confirmed_min_price": 95,
        "confirmed_max_price": 120,
        "delivery_window": "2-4 weeks",
        "moq": 50
    }
    """

    mi = db.query(MarketIntention).filter(
        MarketIntention.id == market_intention_id
    ).first()

    if not mi:
        return {"error": "Market intention not found"}

    if mi.dct_status != "confirmed":
        return {"error": "DCT not confirmed"}

    existing = db.query(MerchantCommitment).filter(
        MerchantCommitment.market_intention_id == market_intention_id,
        MerchantCommitment.merchant_id == payload["merchant_id"],
    ).first()

    if existing:
        return {"error": "Commitment already exists"}

    commitment = MerchantCommitment(
        market_intention_id=market_intention_id,
        merchant_id=payload["merchant_id"],
        capacity=payload["capacity"],
        confirmed_min_price=payload["confirmed_min_price"],
        confirmed_max_price=payload["confirmed_max_price"],
        delivery_window=payload["delivery_window"],
        moq=payload.get("moq"),
        status="ready",
    )

    db.add(commitment)
    db.commit()

    return {"status": "commitment_created"}
