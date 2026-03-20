from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.sql import func
from db import Base

class MarketEvent(Base):
    __tablename__ = "market_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(64), index=True, nullable=False)
    category = Column(String(128), index=True, nullable=False)

    gi = Column(Float, nullable=True)
    rho = Column(Float, nullable=True)
    vn = Column(Float, nullable=True)
    cc = Column(Float, nullable=True)

    payload_json = Column(Text, nullable=True)

    processed = Column(Boolean, default=False, index=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    process_notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
