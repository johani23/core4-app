# ============================================================================
# 🧪 Tribe Audit API — Governor Only
# ============================================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.tribe_signal import TribeSignal
from database import get_db
import uuid

router = APIRouter(prefix="/api/tribes", tags=["tribes"])

WEIGHTS = {
    "contextual_utility": 0.20,
    "mobility_cost": 0.15,
    "longevity": 0.15,
    "regret Spoil": 0.20,
    "integrity": 0.15,
    "value_per_year": 0.15,
}

@router.post("/audit")
def audit_product(payload: dict, db: Session = Depends(get_db)):
    scores = payload["scores"]

    weighted = sum(scores[k] * WEIGHTS[k] for k in WEIGHTS)
    context_fit = weighted / 5
    regret_risk = (6 - scores["regret_risk"]) / 5

    integrity_flag = scores["integrity"] < 3

    if integrity_flag:
        state = "flagged"
    elif context_fit > 0.75:
        state = "trusted"
    else:
        state = "neutral"

    signal = TribeSignal(
        id=str(uuid.uuid4()),
        tribe_id=payload["tribe_id"],
        product_id=payload["product_id"],
        context_fit_score=context_fit,
        regret_risk=regret_risk,
        value_per_year="high" if scores["value_per_year"] >= 4 else "medium",
        integrity_flag=integrity_flag,
        eligibility_state=state,
    )

    db.add(signal)
    db.commit()

    return {"status": "ok", "eligibility_state": state}
