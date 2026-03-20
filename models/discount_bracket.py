# ====================================================================
# 💚 Core4.AI – Discount Bracket Model (FINAL CLEAN)
# ====================================================================

from sqlalchemy import Column, Integer, Float, ForeignKey, String
from db import Base


class DiscountBracket(Base):

    __tablename__ = "discount_brackets"

    id = Column(Integer, primary_key=True, index=True)

    # -------------------------------------------------
    # Linked to Campaign (NOT offer)
    # -------------------------------------------------
    campaign_id = Column(
        Integer,
        ForeignKey("campaigns.id"),
        nullable=False,
        index=True
    )

    # -------------------------------------------------
    # Display name
    # -------------------------------------------------
    name = Column(String(50), nullable=False)

    # -------------------------------------------------
    # Unlock condition
    # -------------------------------------------------
    required_commitments = Column(
        Integer,
        nullable=False
    )

    # -------------------------------------------------
    # Discount %
    # -------------------------------------------------
    discount_percent = Column(
        Float,
        nullable=True
    )

    # -------------------------------------------------
    # Final price
    # -------------------------------------------------
    price = Column(
        Float,
        nullable=False
    )

    # -------------------------------------------------
    # Order
    # -------------------------------------------------
    rank = Column(
        Integer,
        default=0
    )