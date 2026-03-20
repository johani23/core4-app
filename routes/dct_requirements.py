from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from db import get_db
from models.dct_requirement import DCTRequirement

router = APIRouter(
    prefix="/dct/requirements",
    tags=["dct-requirements"]
)


@router.get("/initiator/{initiator_key}")
def list_initiator_requirements(initiator_key: str, db: Session = Depends(get_db)):
    """
    Tribe leader checks what DCT confirmations are pending.
    """
    rows = (
        db.query(DCTRequirement)
        .filter(DCTRequirement.initiator_key == initiator_key)
        .order_by(DCTRequirement.created_at.desc())
        .all()
    )

    return [
        {
            "id": r.id,
            "market_intention_id": r.market_intention_id,
            "initiator_key": r.initiator_key,
            "status": r.status,
            "timing_window": r.timing_window,
            "target_price": r.target_price,
            "max_price": r.max_price,
            "discount_brackets": r.discount_brackets,
            "created_at": r.created_at,
            "updated_at": r.updated_at,
        }
        for r in rows
    ]


@router.post("/{market_intention_id}/confirm")
def confirm_dct_requirements(market_intention_id: int, payload: dict, db: Session = Depends(get_db)):
    """
    Tribe leader confirms DCT dimensions.

    payload:
    {
      "initiator_key": "tribe_leader_1",
      "timing_window": "soon",
      "target_price": 120,
      "max_price": 150,
      "discount_brackets": [
        {"min_qty":1, "max_qty":10, "discount_pct":0},
        {"min_qty":11, "max_qty":50, "discount_pct":5},
        {"min_qty":51, "max_qty": null, "discount_pct":10}
      ]
    }
    """

    initiator_key = payload.get("initiator_key")
    if not initiator_key:
        return {"error": "initiator_key is required"}

    timing_window = payload.get("timing_window")
    target_price = payload.get("target_price")
    max_price = payload.get("max_price")
    discount_brackets = payload.get("discount_brackets")

    # Hard requirements
    if not timing_window:
        return {"error": "timing_window is required"}
    if target_price is None or max_price is None:
        return {"error": "target_price and max_price are required"}
    if not isinstance(discount_brackets, list) or len(discount_brackets) == 0:
        return {"error": "discount_brackets must be a non-empty list"}

    req = (
        db.query(DCTRequirement)
        .filter(DCTRequirement.market_intention_id == market_intention_id)
        .first()
    )
    if not req:
        return {"error": "DCT requirement not found for this market_intention_id"}

    # Security-lite for pilot: enforce same initiator
    if req.initiator_key != initiator_key:
        return {"error": "initiator_key mismatch"}

        req.timing_window = timing_window
    req.target_price = float(target_price)
    req.max_price = float(max_price)
    req.discount_brackets = discount_brackets
    req.status = "confirmed"
    req.updated_at = datetime.utcnow()

    # 🔥 Sync with MarketIntention
    mi = (
        db.query(MarketIntention)
        .filter(MarketIntention.id == market_intention_id)
        .first()
    )

    if mi:
        mi.dct_status = "confirmed"

    db.commit()

    return {"status": "confirmed", "market_intention_id": market_intention_id}

