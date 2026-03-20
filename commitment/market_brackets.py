# commitment/market_brackets.py

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime,
    ForeignKey, Float, Boolean,
    UniqueConstraint, Index
)
from db import Base


class MarketBracket(Base):
    __tablename__ = "market_brackets"

    id = Column(Integer, primary_key=True, index=True)

    market_intention_id = Column(
        Integer,
        ForeignKey("market_intentions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Threshold
    required_commitments = Column(Integer, nullable=False)

    # Action type
    unlock_type = Column(
        String(32),
        nullable=False
        # DISCOUNT | SUMMON | CAMPAIGN | GOVERNANCE
    )

    # Optional numeric value (e.g. discount %)
    value = Column(Float, nullable=True)

    rank = Column(Integer, default=0, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint(
            "market_intention_id",
            "rank",
            name="uq_market_bracket_rank"
        ),
        Index(
            "ix_market_bracket_intention",
            "market_intention_id"
        ),
    )
