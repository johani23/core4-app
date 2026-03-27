# ====================================================================
# 💚 Core4.AI – Discount Bracket Model (PRODUCTION CLEAN)
# ====================================================================

from sqlalchemy import Column, Integer, Float, ForeignKey
from db import Base


class DiscountBracket(Base):

    __tablename__ = "discount_brackets"

    id = Column(Integer, primary_key=True, index=True)

    # -------------------------------------------------
    # Link to Campaign (SOURCE OF TRUTH)
    # -------------------------------------------------
    campaign_id = Column(
        Integer,
        ForeignKey("campaigns.id"),
        nullable=False,
        index=True
    )

    # -------------------------------------------------
    # Unlock condition (MANDATORY)
    # -------------------------------------------------
    required_commitments = Column(
        Integer,
        nullable=False
    )

    # -------------------------------------------------
    # Final price at this level (MANDATORY)
    # -------------------------------------------------
    price = Column(
        Float,
        nullable=False
    )

    # -------------------------------------------------
    # Optional: ordering control (safe to keep)
    # -------------------------------------------------
    rank = Column(
        Integer,
        default=0
    )