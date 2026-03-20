# ============================================================================
# 🟠 Core4.AI – Merchant Demand Signals
# Merchant reads qualified demand opportunities
# ============================================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db

from models.demand_signal_log import DemandSignalLog
from models.market_intention import MarketIntention

router = APIRouter(
    prefix="/merchant/demand-signals",
    tags=["merchant-demand-signals"]
)


@router.get("/{merchant_id}")
def get_merchant_demand_signals(
    merchant_id: int,
    db: Session = Depends(get_db)
):
    logs = (
        db.query(DemandSignalLog, MarketIntention)
        .join(
            MarketIntention,
            DemandSignalLog.market_intention_id == MarketIntention.id
        )
        .filter(
            DemandSignalLog.merchant_id == merchant_id,
            DemandSignalLog.visible == True,
            MarketIntention.qualified == True,
        )
        .order_by(DemandSignalLog.created_at.desc())
        .all()
    )

    return [
        {
            "log_id": log.id,
            "market_intention_id": mi.id,
            "feature_text": mi.feature_text,
            "normalized_features": mi.normalized_features,
            "target_price": mi.target_price,
            "max_price": mi.max_price,
            "quantity_interest": mi.quantity_interest,
            "time_horizon": mi.time_horizon,
            "signal_score": mi.signal_score,
            "qualification_reason": mi.qualification_reason,
            "created_at": mi.created_at,

            # 🔥 IMPORTANT
            "dct_status": mi.dct_status,
        }
        for log, mi in logs
    ]
