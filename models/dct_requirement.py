from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    JSON,
    ForeignKey,
    UniqueConstraint,
)
from datetime import datetime
from db import Base


class DCTRequirement(Base):
    """
    DCT v1.1 — Demand Confirmation Trigger

    Created when the FIRST merchant marks a MarketIntention as "Interested".

    Purpose:
    - Capture contextual commitment (NOT a purchase)
    - Require Tribe Leader confirmation on:
        * Timing
        * Price intent
        * Discount brackets

    IMPORTANT:
    - This is NOT a contract
    - This is NOT a financial obligation
    """

    __tablename__ = "dct_requirements"

    id = Column(Integer, primary_key=True, index=True)

    # ------------------------------------------------------------------
    # Link to Market Intention
    # ------------------------------------------------------------------
    market_intention_id = Column(
        Integer,
        ForeignKey("market_intentions.id"),
        nullable=False,
        index=True,
    )

    # Tribe Leader / Demand Initiator
    initiator_key = Column(String, nullable=False, index=True)

    # ------------------------------------------------------------------
    # DCT lifecycle
    # ------------------------------------------------------------------
    status = Column(
        String,
        default="pending",  # pending | confirmed | expired
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Required confirmation dimensions
    # ------------------------------------------------------------------
    timing_window = Column(
        String,
        nullable=True,
        doc="now | soon | later | custom",
    )

    target_price = Column(Float, nullable=True)
    max_price = Column(Float, nullable=True)

    # Discount brackets example:
    # [
    #   {"min_qty": 1,  "max_qty": 10,  "discount_pct": 0},
    #   {"min_qty": 11, "max_qty": 50,  "discount_pct": 5},
    #   {"min_qty": 51, "max_qty": null,"discount_pct": 10}
    # ]
    discount_brackets = Column(JSON, nullable=True)

    # ------------------------------------------------------------------
    # Audit timestamps
    # ------------------------------------------------------------------
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    __table_args__ = (
        # Enforce ONE DCT per Market Intention
        UniqueConstraint(
            "market_intention_id",
            name="uq_dct_requirement_market_intention",
        ),
    )
