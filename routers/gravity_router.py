# ============================================================================
# 💠 Gravity API Router
# Emits Demand Events Automatically
# ============================================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import get_db
from gravity.gravity import evaluate_category
from services.event_bus import emit_event


router = APIRouter(
    prefix="/api/gravity",
    tags=["gravity"],
)


@router.post("/evaluate/{category}")
def evaluate(category: str, db: Session = Depends(get_db)):

    # ---------------------------------
    # 1️⃣ Run Gravity Engine
    # ---------------------------------
    state = evaluate_category(db, category)

    gi = state["gi"]
    rho = state["rho"]
    vn = state["vn"]
    cc = state["cc"]
    mode = state["mode"]

    # ---------------------------------
    # 2️⃣ Emit Market Events (MVP Rules)
    # ---------------------------------

    # Strong demand
    if gi >= 0.80:
        emit_event(
            db=db,
            event_type="GRAVITY_SPIKE",
            category=category,
            gi=gi,
            rho=rho,
            vn=vn,
            cc=cc,
            payload={"mode": mode},
        )

    # High volatility
    if rho >= 0.60:
        emit_event(
            db=db,
            event_type="VOLATILITY_HIGH",
            category=category,
            gi=gi,
            rho=rho,
            vn=vn,
            cc=cc,
            payload={"mode": mode},
        )

    # ---------------------------------
    # 3️⃣ Return Gravity Metrics
    # ---------------------------------
    return state
