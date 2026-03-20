import uuid
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.merchant_offer import MerchantOffer
from models.pricing_action import PricingAction

def apply_pricing_action(
    db: Session,
    category: str,
    action_type: str,
    delta_pct: float,
    event_id: int,
    reason: str,
):
    trace_id = uuid.uuid4().hex[:16]

    offer = db.query(MerchantOffer).filter(MerchantOffer.category == category).first()
    if not offer:
        offer = MerchantOffer(category=category, base_price=100.0, current_price=100.0)
        db.add(offer)
        db.commit()
        db.refresh(offer)

    old_price = float(offer.current_price)
    new_price = old_price * (1.0 + float(delta_pct))

    # MVP guard rails (no negative / no extreme changes)
    if new_price < 1.0:
        new_price = 1.0
    if new_price > old_price * 1.50:
        new_price = old_price * 1.50

    offer.current_price = new_price

    action = PricingAction(
        category=category,
        action_type=action_type,
        delta_pct=delta_pct,
        old_price=old_price,
        new_price=new_price,
        event_id=event_id,
        trace_id=trace_id,
        reason=reason,
    )

    try:
        db.add(action)
        db.commit()
        db.refresh(action)
        return action
    except SQLAlchemyError as e:
        db.rollback()
        raise RuntimeError(f"apply_pricing_action failed: {e}")
