from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from db import Base

class PricingAction(Base):
    __tablename__ = "pricing_actions"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(128), index=True, nullable=False)
    action_type = Column(String(64), nullable=False)  # e.g., PRICE_UP, PRICE_DOWN, PROMO_ON
    delta_pct = Column(Float, nullable=True)
    old_price = Column(Float, nullable=True)
    new_price = Column(Float, nullable=True)

    event_id = Column(Integer, nullable=False)
    trace_id = Column(String(64), index=True, nullable=False)
    reason = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
