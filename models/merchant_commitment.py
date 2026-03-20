from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from datetime import datetime
from db import Base


class MerchantCommitment(Base):
    """
    Soft execution commitment by merchant.
    Created ONLY if DCT is confirmed.
    """

    __tablename__ = "merchant_commitments"

    id = Column(Integer, primary_key=True, index=True)

    market_intention_id = Column(
        Integer,
        ForeignKey("market_intentions.id"),
        nullable=False,
        index=True,
    )

    merchant_id = Column(Integer, nullable=False, index=True)

    # Execution readiness
    capacity = Column(Integer, nullable=False)
    confirmed_min_price = Column(Float, nullable=False)
    confirmed_max_price = Column(Float, nullable=False)
    delivery_window = Column(String, nullable=False)  # e.g. "2-4 weeks"
    moq = Column(Integer, nullable=True)

    status = Column(String, default="ready")  # ready | paused | withdrawn

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint(
            "market_intention_id",
            "merchant_id",
            name="uq_commitment_market_merchant",
        ),
    )
