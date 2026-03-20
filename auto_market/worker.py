from sqlalchemy.orm import Session

from commitment.models import MerchantOffer, DiscountBracket
from gravity.service import get_gravity_index


GRAVITY_THRESHOLD = 1.5


def campaign_exists(db: Session, sku: str) -> bool:
    return (
        db.query(MerchantOffer)
        .filter(
            MerchantOffer.sku == sku,
            MerchantOffer.is_active == True
        )
        .first()
        is not None
    )


def create_discount_brackets(db: Session, offer_id: int):
    brackets = [
        ("tier1", 10, 4, 1),
        ("tier2", 30, 7, 2),
        ("tier3", 60, 10, 3),
        ("tier4", 100, 17, 4),
    ]

    for name, required, discount, rank in brackets:
        b = DiscountBracket(
            offer_id=offer_id,
            name=name,
            required_commitments=required,
            discount_percent=discount,
            rank=rank,
        )
        db.add(b)

    db.commit()


def create_auto_campaign(
    db: Session,
    title: str,
    sku: str,
    base_price: float,
    currency: str = "USD",
):
    offer = MerchantOffer(
        merchant_id="auto_market",
        title=title,
        sku=sku,
        currency=currency,
        base_price=base_price,
        is_active=True,
    )

    db.add(offer)
    db.commit()
    db.refresh(offer)

    create_discount_brackets(db, offer.id)

    return offer


def run_auto_market_engine(db: Session, category: str, title: str, sku: str, base_price: float):

    gravity = get_gravity_index(category)

    if gravity < GRAVITY_THRESHOLD:
        return None

    if campaign_exists(db, sku):
        return None

    offer = create_auto_campaign(
        db=db,
        title=title,
        sku=sku,
        base_price=base_price,
    )

    return offer