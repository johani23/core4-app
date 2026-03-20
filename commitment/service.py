# ====================================================================
# 🧠 Core4.AI – Commitment Engine Service (PRODUCTION SAFE + GROWTH)
# ====================================================================

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

# Models
from commitment.models import Commitment
from models.discount_bracket import DiscountBracket
from models.merchant_offer import MerchantOffer

# 🚀 Growth
from services.growth_logger import log_event


# =========================================================
# COMPUTE ENGINE STATE
# =========================================================

def compute_engine_state(db: Session, offer_id: int, mode: str = "COUNT"):

    commitments_count = db.query(func.count(Commitment.id)).filter(
        Commitment.offer_id == offer_id,
        Commitment.is_active == True
    ).scalar()

    offer = db.query(MerchantOffer).filter(
        MerchantOffer.id == offer_id
    ).first()

    if not offer:
        raise ValueError("Offer not found")

    brackets = db.query(DiscountBracket).filter(
        DiscountBracket.campaign_id == offer.campaign_id
    ).order_by(DiscountBracket.rank.asc()).all()

    active_bracket = 0
    current_price = None
    bracket_states = []

    for i, b in enumerate(brackets):

        unlocked = commitments_count >= b.required_commitments

        if unlocked:
            active_bracket = i + 1
            current_price = b.price

        bracket_states.append({
            "id": b.id,
            "name": b.name,
            "required_commitments": b.required_commitments,
            "discount_percent": b.discount_percent,
            "rank": b.rank,
            "unlocked": unlocked
        })

    if current_price is None:
        if brackets:
            current_price = brackets[0].price
        else:
            current_price = offer.base_price

    return {
        "offer_id": offer_id,
        "commitments_count": commitments_count,
        "active_bracket": active_bracket,
        "brackets": bracket_states,
        "current_price": current_price
    }


# =========================================================
# UPSERT COMMITMENT (RACE SAFE + GROWTH TRACKING)
# =========================================================

def upsert_commitment(
    db: Session,
    offer_id: int,
    buyer_id: str,
    quantity: int,
    commitment_type: str,
):

    try:
        new_commitment = Commitment(
            offer_id=offer_id,
            buyer_id=buyer_id,
            quantity=quantity,
            commitment_type=commitment_type,
            is_active=True,
        )

        db.add(new_commitment)
        db.commit()
        db.refresh(new_commitment)

        # 🚀 Growth Event (NEW JOIN)
        log_event(
            db=db,
            event_type="commitment_joined",
            user_id=buyer_id,
            metadata={
                "offer_id": offer_id,
                "quantity": quantity,
                "type": "new"
            }
        )

        return new_commitment

    except IntegrityError:
        db.rollback()

        existing = db.query(Commitment).filter(
            Commitment.offer_id == offer_id,
            Commitment.buyer_id == buyer_id
        ).first()

        if not existing:
            raise

        existing.quantity = quantity
        existing.commitment_type = commitment_type
        existing.is_active = True

        db.commit()
        db.refresh(existing)

        # 🚀 Growth Event (UPDATE / RE-ENGAGEMENT)
        log_event(
            db=db,
            event_type="commitment_joined",
            user_id=buyer_id,
            metadata={
                "offer_id": offer_id,
                "quantity": quantity,
                "type": "update"
            }
        )

        return existing


# =========================================================
# CANCEL COMMITMENT
# =========================================================

def cancel_commitment(db: Session, offer_id: int, buyer_id: str):

    commitment = db.query(Commitment).filter(
        Commitment.offer_id == offer_id,
        Commitment.buyer_id == buyer_id
    ).first()

    if not commitment:
        raise ValueError("Commitment not found")

    commitment.is_active = False
    db.commit()

    # 🚀 Optional Growth Event (drop-off signal)
    log_event(
        db=db,
        event_type="commitment_cancelled",
        user_id=buyer_id,
        metadata={
            "offer_id": offer_id
        }
    )

    return commitment