# ====================================================================
# 💚 Core4.AI – Commitment Models (FINAL HARDENED)
# ====================================================================

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime,
    Boolean, ForeignKey, UniqueConstraint, Index
)
from db import Base


# =========================================================
# 📊 DISCOUNT BRACKETS (offer-level)
# =========================================================

class OfferDiscountBracket(Base):

    __tablename__ = "offer_discount_brackets"

    id = Column(Integer, primary_key=True, index=True)

    offer_id = Column(
        Integer,
        ForeignKey("merchant_offers.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    name = Column(String(50), nullable=False)

    required_commitments = Column(Integer, nullable=False)

    discount_percent = Column(Float, nullable=True)

    price = Column(Float, nullable=False)

    rank = Column(Integer, default=0, nullable=False)

    __table_args__ = (
        Index("ix_offer_bracket_offer_rank", "offer_id", "rank"),
    )


# =========================================================
# 🧠 COMMITMENT ENGINE (offer-level commitments)
# =========================================================

class Commitment(Base):

    __tablename__ = "commitments"

    id = Column(Integer, primary_key=True, index=True)

    offer_id = Column(
        Integer,
        ForeignKey("merchant_offers.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    buyer_id = Column(String(64), nullable=False, index=True)

    quantity = Column(Integer, default=1, nullable=False)

    commitment_type = Column(String(16), default="SOFT", nullable=False)

    weight = Column(Float, default=1.0, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint(
            "offer_id",
            "buyer_id",
            name="uq_commitment_offer_buyer"
        ),
        Index("ix_commitment_offer_active", "offer_id", "is_active"),
    )


# =========================================================
# 💚 CAMPAIGN COMMITMENTS (Buyer Join Layer)
# =========================================================

class MarketCommitment(Base):

    __tablename__ = "market_commitments"

    id = Column(Integer, primary_key=True, index=True)

    campaign_id = Column(
        Integer,
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    email = Column(
        String(120),
        nullable=False,
        index=True
    )

    commitment_price = Column(
        Float,
        nullable=False
    )

    first_name = Column(String(100), nullable=True)

    city = Column(String(100), nullable=True)

    # =====================================================
    # 🔥 REFERRAL SYSTEM
    # =====================================================

    referral_code = Column(
        String(20),
        nullable=False,
        index=True
    )

    referred_by = Column(
        String(20),
        nullable=True,
        index=True
    )

    # =====================================================
    # STATUS
    # =====================================================

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True   # ✅ important for recent joins queries
    )

    __table_args__ = (

        # 🔥 CRITICAL: prevent duplicate joins
        UniqueConstraint(
            "campaign_id",
            "email",
            name="uq_market_commitment_campaign_email"
        ),

        # 🔥 referral code unique per campaign (NOT global)
        UniqueConstraint(
            "campaign_id",
            "referral_code",
            name="uq_campaign_referral_code"
        ),

        # ⚡ fast active lookups
        Index(
            "ix_market_commitment_active",
            "campaign_id",
            "is_active"
        ),

        # ⚡ referral analytics
        Index(
            "ix_market_commitment_referral",
            "campaign_id",
            "referred_by"
        ),
    )