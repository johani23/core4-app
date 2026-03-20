from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db import get_db

from engines.market_intelligence_engine import evaluate_market_intelligence

router = APIRouter(
    prefix="/merchant",
    tags=["merchant-intelligence"]
)


@router.get("/market-intelligence/{market_intention_id}")
def market_intelligence(
    market_intention_id: int,
    category: str = Query(..., description="Category for Gravity evaluation"),
    db: Session = Depends(get_db),
):
    return evaluate_market_intelligence(db, market_intention_id, category)