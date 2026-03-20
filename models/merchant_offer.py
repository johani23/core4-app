# ====================================================================
# 🏪 Core4.AI – Merchant Offer Model (PRODUCTION READY)
# ====================================================================

from sqlalchemy import (
    Column,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    Boolean,
    String,
    UniqueConstraint,
    Index
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from db import Base


class MerchantOffer(Base):

    __tablename__ = "merchant_offers"

    id = Column(Integer, primary_key=True, index=True)

    # -------------------------------------------------
    # Campaign
    # -------------------------------------------------
    campaign_id = Column(
        Integer,
        ForeignKey("campaigns.id"),
        nullable=False,
        index=True
    )

    # -------------------------------------------------
    # Merchant
    # -------------------------------------------------
    merchant_id = Column(
        String(64),
        nullable=False,
        index=True
    )

    # -------------------------------------------------
    # Product Info
    # -------------------------------------------------
    title = Column(String(200), nullable=False)

    sku = Column(String(80), nullable=True)

    currency = Column(String(8), default="SAR", nullable=False)

    # -------------------------------------------------
    # Pricing
    # -------------------------------------------------
    base_price = Column(Float, nullable=False)

    current_price = Column(Float, nullable=False)

    # -------------------------------------------------
    # Status
    # -------------------------------------------------
    is_active = Column(Boolean, default=True, nullable=False)

    # -------------------------------------------------
    # Audit
    # -------------------------------------------------
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # -------------------------------------------------
    # Constraints + Indexes
    # -------------------------------------------------
    __table_args__ = (
        # 🚨 Prevent duplicate offers per merchant per campaign
        UniqueConstraint(
            "merchant_id",
            "campaign_id",
            name="uq_merchant_campaign_offer"
        ),

        # ⚡ Fast lookup for active offers in a campaign
        Index(
            "ix_offer_campaign_active",
            "campaign_id",
            "is_active"
        ),
    )