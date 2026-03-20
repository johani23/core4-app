# ============================================================================
# 🛡 Tribe Approval API — Create TribeSignal
# ============================================================================

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from db import get_db
from models.tribe_signal import TribeSignal

router = APIRouter(
    prefix="/api/tribe",
    tags=["tribe-approval"]
)

@router.post("/approve/{product_id}")
def approve_product_by_tribe(
    product_id: int,
    tribe_id: str = "default_tribe",
    db: Session = Depends(get_db),
):
    """
    Human-in-the-loop approval that creates a TribeSignal.
    """

    signal = TribeSignal(
        id=f"{tribe_id}_{product_id}_{int(datetime.utcnow().timestamp())}",
        tribe_id=tribe_id,
        product_id=str(product_id),
        context_fit_score=0.9,
        regret_risk=0.1,
        value_per_year="high",
        integrity_flag=False,
        eligibility_state="trusted",
        evaluated_at=datetime.utcnow(),
    )

    db.add(signal)
    db.commit()

    return {
        "status": "approved",
        "product_id": product_id,
        "tribe_id": tribe_id,
        "eligibility_state": "trusted",
    }
