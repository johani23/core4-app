from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from db import Base

class ElasticityState(Base):
    __tablename__ = "elasticity_states"

    id = Column(Integer, primary_key=True, index=True)
    market_id = Column(String, unique=True, index=True, nullable=False)

    # EWMA of conversion rate (or orders per hour if no visits)
    conv_ewma = Column(Float, default=0.0)

    # A simple elasticity indicator: higher => more price sensitive
    elasticity = Column(Float, default=1.0)

    # last observed applied price
    last_price = Column(Float, default=0.0)

    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
