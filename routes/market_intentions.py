# ============================================================================
# 🔵 Core4.AI – Market Intentions API
# Buyer creates demand • Merchant reads opportunities
# ============================================================================
# RULES:
# - Explicit demand only (not behavioral signals)
# - Qualification happens ONCE at creation time
# - Fan-out is explicit and auditable
# - DCT context is linked, not embedded
# ============================================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import json

from db import get_db
from models.market_intention import MarketIntention
from models.demand_signal_log import DemandSignalLog

# 🔹 Domain logic (PURE)
from app.domain.demand_qualification import qualify_signal

QUALIFICATION_THRESHOLD = 25

router = APIRouter(
    prefix="/market-intentions",
    tags=["market-intentions"]
)

# ----------------------------------------------------------------------------
# CREATE INTENTION (Tribe Leader declares demand)
# ----------------------------------------------------------------------------
@router.post("/")
def create_intention(payload: dict, db: Session = Depends(get_db)):

    # ------------------------------------------------------------------------
    # 1️⃣ Create demand record
    # ------------------------------------------------------------------------
    intention = MarketIntention(
        feature_text=payload.get("feature_text"),
        normalized_features=payload.get("normalized_features", []),
        target_price=payload.get("target_price", 0),
        max_price=payload.get("max_price", 0),
        quantity_interest=payload.get("quantity_interest", 1),
        time_horizon=payload.get("time_horizon"),
        buyer_cluster=payload.get("buyer_cluster"),
        initiator_key=payload.get("initiator_key") or payload.get("buyer_cluster"),
        dct_status="none",
        status="open",
    )

    db.add(intention)

    # ------------------------------------------------------------------------
    # 2️⃣ Qualification (ONCE)
    # ------------------------------------------------------------------------
    result = qualify_signal(
        tribe_interests=payload.get("normalized_features", []),
        audience_interests=payload.get("normalized_features", []),
        budget_min=payload.get("target_price", 0),
        budget_max=payload.get("max_price", 0),
        timeframe=payload.get("time_horizon"),
        threshold=QUALIFICATION_THRESHOLD,
    )

    intention.signal_score = result["score"]
    intention.qualified = result["qualified"]
    intention.qualification_reason = result["reason"]
    intention.score_components = json.dumps(result["components"])

    # ------------------------------------------------------------------------
    # 3️⃣ Persist Market Intention
    # ------------------------------------------------------------------------
    db.commit()
    db.refresh(intention)

    # ------------------------------------------------------------------------
    # 4️⃣ Fan-out to Merchant Layer (TEMP: merchant_id = 1)
    # ------------------------------------------------------------------------
    if intention.qualified:
        log = DemandSignalLog(
            market_intention_id=intention.id,
            merchant_id=1,   # TEMP until merchant auth/registry
            visible=True,
        )
        db.add(log)
        db.commit()

    return {
        "status": "created",
        "id": intention.id,
        "qualified": intention.qualified,
        "signal_score": intention.signal_score,
        "dct_status": intention.dct_status,
    }

# ----------------------------------------------------------------------------
# LIST OPEN & QUALIFIED INTENTIONS (debug / admin)
# ----------------------------------------------------------------------------
@router.get("/")
def list_intentions(db: Session = Depends(get_db)):
    intentions = (
        db.query(MarketIntention)
        .filter(
            MarketIntention.status == "open",
            MarketIntention.qualified == True,
        )
        .order_by(MarketIntention.created_at.desc())
        .all()
    )

    return [
        {
            "id": i.id,
            "feature_text": i.feature_text,
            "normalized_features": i.normalized_features,
            "target_price": i.target_price,
            "max_price": i.max_price,
            "quantity_interest": i.quantity_interest,
            "time_horizon": i.time_horizon,
            "buyer_cluster": i.buyer_cluster,
            "initiator_key": i.initiator_key,
            "signal_score": i.signal_score,
            "qualification_reason": i.qualification_reason,
            "dct_status": i.dct_status,
            "created_at": i.created_at,
        }
        for i in intentions
    ]
