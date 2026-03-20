from sqlalchemy.orm import Session

from models.campaign import Campaign
from models.product import Product
from models.discount_bracket import DiscountBracket


def campaign_exists(db: Session, category: str):
    """
    Check if there is already an active campaign for any product in this category.
    """
    return (
        db.query(Campaign)
        .join(Product, Campaign.product_id == Product.id)
        .filter(
            Product.category == category,
            Campaign.status == "نشطة"
        )
        .first()
    )


def get_product_for_category(db: Session, category: str):
    """
    Pick one product from the category to attach the campaign to.
    MVP behavior: first matching product.
    """
    return (
        db.query(Product)
        .filter(Product.category == category)
        .order_by(Product.id.asc())
        .first()
    )


def create_auto_campaign(db: Session, category: str):
    """
    Create campaign automatically when gravity enters SUMMONS mode.
    Uses the existing Campaign schema in your project.
    """

    existing = campaign_exists(db, category)
    if existing:
        print(f"[AutoCampaign] campaign already exists for category={category}")
        return existing

    product = get_product_for_category(db, category)
    if not product:
        raise ValueError(f"No product found for category={category}")

    campaign = Campaign(
        product_id=product.id,
        intention_id=None,
        channel="auto_gravity",
        context_note=f"Auto-created from gravity for category={category}",
        status="نشطة",
    )

    db.add(campaign)
    db.commit()
    db.refresh(campaign)

    print(
        f"[AutoCampaign] created campaign id={campaign.id} "
        f"for category={category} product_id={product.id}"
    )

    base_price = float(getattr(product, "price", 1000) or 1000)

    brackets = [
        (10, 3),
        (30, 7),
        (60, 10),
        (100, 18),
    ]

    for required, discount in brackets:
        unlock_price = round(base_price * (1 - discount / 100.0), 2)

        b = DiscountBracket(
            campaign_id=campaign.id,
            required_commitments=required,
            discount_percent=discount,
            price=unlock_price,
        )

        db.add(b)

    db.commit()

    print(f"[AutoCampaign] created brackets for campaign_id={campaign.id}")

    return campaign