# routes/merchant/demand_metrics.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from db import get_db
from models.merchant_response import MerchantResponse

router = APIRouter(
    prefix="/merchant/demand-metrics",
    tags=["merchant-demand-metrics"]
)

@router.get("/{market_intention_id}")
def metrics(market_intention_id: int, db: Session = Depends(get_db)):
    rows = (
        db.query(MerchantResponse.action, func.count().label("c"))
        .filter(MerchantResponse.market_intention_id == market_intention_id)
        .group_by(MerchantResponse.action)
        .all()
    )
    return {a: c for a, c in rows}
