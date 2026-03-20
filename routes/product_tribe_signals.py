# ============================================================================
# 👤 Buyer Trust Signal (READ ONLY)
// ============================================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.tribe_signal import TribeSignal
from database import get_db

router = APIRouter(tags=["products"])

@router.get("/api/products/{product_id}/tribe-signals")
def get_signals(product_id: str, db: Session = Depends(get_db)):
    signal = (
        db.query(TribeSignal)
        .filter(TribeSignal.product_id == product_id)
        .order_by(TribeSignal.evaluated_at.desc())
        .first()
    )

    if not signal:
        return {}

    return {
        "tribe": signal.tribe_id,
        "eligibility_state": signal.eligibility_state,
        "value_per_year": signal.value_per_year,
    }
