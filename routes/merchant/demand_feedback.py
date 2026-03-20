from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import get_db
from models.merchant_response import MerchantResponse
from models.market_intention import MarketIntention
from models.dct_requirement import DCTRequirement

router = APIRouter(
    prefix="/merchant/demand-feedback",
    tags=["merchant-demand-feedback"]
)

@router.post("/")
def submit_feedback(payload: dict, db: Session = Depends(get_db)):
    """
    payload:
    {
      "merchant_id": 1,
      "market_intention_id": 2,
      "action": "viewed | interested | not_fit",
      "note": "optional"
    }
    """

    merchant_id = payload["merchant_id"]
    mi_id = payload["market_intention_id"]
    action = payload["action"]
    note = payload.get("note")

    # ------------------------------------------------------------
    # 1) Upsert MerchantResponse (idempotent)
    # ------------------------------------------------------------
    existing = (
        db.query(MerchantResponse)
        .filter_by(
            merchant_id=merchant_id,
            market_intention_id=mi_id
        )
        .first()
    )

    if existing:
        existing.action = action
        existing.note = note
    else:
        db.add(MerchantResponse(
            merchant_id=merchant_id,
            market_intention_id=mi_id,
            action=action,
            note=note
        ))

    db.commit()

    # ------------------------------------------------------------
    # 2) DCT Trigger (FIRST interested only)
    # ------------------------------------------------------------
    if action == "interested":
        mi = (
            db.query(MarketIntention)
            .filter(MarketIntention.id == mi_id)
            .first()
        )

        if mi:
            initiator_key = mi.initiator_key or mi.buyer_cluster

            if initiator_key:
                existing_req = (
                    db.query(DCTRequirement)
                    .filter(
                        DCTRequirement.market_intention_id == mi_id
                    )
                    .first()
                )

                # Create DCT only once
                if not existing_req:
                    dct = DCTRequirement(
                        market_intention_id=mi_id,
                        initiator_key=initiator_key,
                        status="pending"
                    )
                    db.add(dct)

                    # Mirror status on MarketIntention (for UI convenience)
                    mi.dct_status = "pending"

                    db.commit()

    return {"status": "ok"}
