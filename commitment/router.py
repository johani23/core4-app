# ====================================================================
# 🚀 Core4.AI – Commitment Router (ROUTER OWNS COMMIT)
# ====================================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_db

from models.merchant_offer import MerchantOffer
from models.discount_bracket import DiscountBracket

from commitment.schemas import (
    OfferCreate,
    OfferOut,
    CommitmentUpsert,
    CommitmentOut,
    EngineState,
)

from commitment.service import (
    compute_engine_state,
    upsert_commitment,
    cancel_commitment,
)

from commitment.market_models import MarketLoopCommitment
from commitment.market_engine import evaluate_market_intention


router = APIRouter(prefix="/api/commitment", tags=["commitment"])


# ====================================================================
# CREATE OR UPDATE OFFER
# ====================================================================
@router.post("/offers", response_model=OfferOut)
def create_offer(payload: OfferCreate, db: Session = Depends(get_db)):

    if payload.base_price <= 0:
        raise HTTPException(status_code=400, detail="base_price must be > 0")

    if not payload.title:
        raise HTTPException(status_code=400, detail="title is required")

    existing_offer = db.query(MerchantOffer).filter(
        MerchantOffer.campaign_id == payload.campaign_id,
        MerchantOffer.merchant_id == payload.merchant_id
    ).first()

    if existing_offer:
        existing_offer.title = payload.title
        existing_offer.sku = payload.sku
        existing_offer.currency = payload.currency
        existing_offer.base_price = payload.base_price
        existing_offer.current_price = payload.base_price
        existing_offer.is_active = True

        if payload.brackets:
            db.query(DiscountBracket).filter(
                DiscountBracket.campaign_id == payload.campaign_id
            ).delete()

            for i, b in enumerate(payload.brackets):
                bracket = DiscountBracket(
                    campaign_id=payload.campaign_id,
                    name=b.name,
                    required_commitments=b.required_commitments,
                    discount_percent=b.discount_percent,
                    price=b.price,
                    rank=i,
                )
                db.add(bracket)

        db.commit()
        db.refresh(existing_offer)
        return existing_offer

    offer = MerchantOffer(
        merchant_id=payload.merchant_id,
        campaign_id=payload.campaign_id,
        title=payload.title,
        sku=payload.sku,
        currency=payload.currency,
        base_price=payload.base_price,
        current_price=payload.base_price,
        is_active=True,
    )

    db.add(offer)

    existing_brackets = db.query(DiscountBracket).filter(
        DiscountBracket.campaign_id == payload.campaign_id
    ).count()

    if existing_brackets == 0 and payload.brackets:
        for i, b in enumerate(payload.brackets):
            bracket = DiscountBracket(
                campaign_id=payload.campaign_id,
                name=b.name,
                required_commitments=b.required_commitments,
                discount_percent=b.discount_percent,
                price=b.price,
                rank=i,
            )
            db.add(bracket)

    db.commit()
    db.refresh(offer)
    return offer


# ====================================================================
# OFFER STATE
# ====================================================================
@router.get("/offers/{offer_id}/state", response_model=EngineState)
def get_offer_state(
    offer_id: int,
    mode: str = "COUNT",
    db: Session = Depends(get_db),
):
    return compute_engine_state(db, offer_id, mode=mode)


# ====================================================================
# COMMIT TO OFFER
# ====================================================================
@router.post("/offers/{offer_id}/commit", response_model=CommitmentOut)
def commit_to_offer(
    offer_id: int,
    payload: CommitmentUpsert,
    db: Session = Depends(get_db),
):
    offer = db.query(MerchantOffer).filter(
        MerchantOffer.id == offer_id
    ).first()

    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    if not payload.buyer_id:
        raise HTTPException(status_code=400, detail="buyer_id required")

    if payload.quantity <= 0:
        raise HTTPException(status_code=400, detail="quantity must be > 0")

    result = upsert_commitment(
        db=db,
        offer_id=offer_id,
        buyer_id=payload.buyer_id,
        quantity=payload.quantity,
        commitment_type=payload.commitment_type,
    )

    db.commit()
    db.refresh(result)

    return result


# ====================================================================
# CANCEL COMMITMENT
# ====================================================================
@router.post("/offers/{offer_id}/cancel/{buyer_id}", response_model=CommitmentOut)
def cancel_offer_commitment(
    offer_id: int,
    buyer_id: str,
    db: Session = Depends(get_db),
):
    result = cancel_commitment(db, offer_id, buyer_id)
    db.commit()
    db.refresh(result)
    return result


# ====================================================================
# MARKET ENGINE
# ====================================================================
@router.post("/market/{market_intention_id}/commit")
def create_market_commitment(
    market_intention_id: int,
    buyer_id: str,
    quantity: int = 1,
    commitment_type: str = "SOFT",
    db: Session = Depends(get_db),
):
    if not buyer_id:
        raise HTTPException(status_code=400, detail="buyer_id required")

    if quantity <= 0:
        raise HTTPException(status_code=400, detail="quantity must be > 0")

    commitment = MarketLoopCommitment(
        market_intention_id=market_intention_id,
        buyer_id=buyer_id,
        quantity=quantity,
        commitment_type=commitment_type,
    )

    db.add(commitment)
    db.commit()
    db.refresh(commitment)

    evaluate_market_intention(db, market_intention_id)

    return {
        "status": "market_commitment_created",
        "market_intention_id": market_intention_id,
        "buyer_id": buyer_id,
    }


@router.get("/market/{market_intention_id}/state")
def get_market_state(
    market_intention_id: int,
    db: Session = Depends(get_db),
):
    return evaluate_market_intention(db, market_intention_id)