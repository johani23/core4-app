from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from db import Base

class PriceExperiment(Base):
    __tablename__ = "price_experiments"

    id = Column(Integer, primary_key=True, index=True)
    market_id = Column(String, index=True, nullable=False)

    proposal_id = Column(Integer, index=True, nullable=False)
    applied_price = Column(Float, nullable=False)

    start_at = Column(DateTime(timezone=True), server_default=func.now())
    end_at = Column(DateTime(timezone=True), nullable=True)

    # observed outcome during window
    orders_count = Column(Integer, default=0)
    visits_count = Column(Integer, default=0)  # optional, can stay 0

    closed = Column(Integer, default=0)  # 0/1

    created_at = Column(DateTime(timezone=True), server_default=func.now())
