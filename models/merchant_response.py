# models/merchant_response.py
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from datetime import datetime
from db import Base

class MerchantResponse(Base):
    __tablename__ = "merchant_responses"

    id = Column(Integer, primary_key=True)
    merchant_id = Column(Integer, index=True, nullable=False)
    market_intention_id = Column(Integer, index=True, nullable=False)
    action = Column(String, nullable=False)  # viewed | interested | not_fit
    note = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("merchant_id", "market_intention_id",
                         name="uq_merchant_intention"),
    )
