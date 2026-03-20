# ============================================================================
# 💚 Core4.AI – Demand Signal Router (STABLE VERSION)
# Logs demand events and keeps demand counter synchronized
# ============================================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from db import get_db
from models.signal import Signal
from models.product import Product

router = APIRouter(tags=["signals"])


# ---------------------------------------------------------------------------
# Request Schema
# ---------------------------------------------------------------------------
class DemandSignalIn(BaseModel):
    post_id: int
    intent: str = "interested"


# ---------------------------------------------------------------------------
# Create Demand Signal
# ---------------------------------------------------------------------------
@router.post("/demand-signal")
def create_demand_signal(
    data: DemandSignalIn,
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------------------------
    # Validate input
    # -----------------------------------------------------------------------
    if not data.post_id:
        raise HTTPException(status_code=400, detail="post_id is required")

    # -----------------------------------------------------------------------
    # Ensure product exists
    # -----------------------------------------------------------------------
    product = db.query(Product).filter(Product.id == data.post_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # -----------------------------------------------------------------------
    # Log demand signal
    # -----------------------------------------------------------------------
    signal = Signal(
        post_id=data.post_id,
        signal_type="demand",
        intent=data.intent,
        confidence=0.6
    )

    db.add(signal)
    db.commit()

    # -----------------------------------------------------------------------
    # Aggregate demand interest
    # -----------------------------------------------------------------------
    interest_count = (
        db.query(Signal)
        .filter(
            Signal.post_id == data.post_id,
            Signal.signal_type == "demand",
            Signal.intent == "interested"
        )
        .count()
    )

    # -----------------------------------------------------------------------
    # Sync counter to product (important for gravity / demand-list)
    # -----------------------------------------------------------------------
    try:
        product.demand_interest = interest_count
        db.commit()
    except Exception:
        db.rollback()

    # -----------------------------------------------------------------------
    # Response
    # -----------------------------------------------------------------------
    return {
        "status": "ok",
        "post_id": data.post_id,
        "interest_count": interest_count
    }