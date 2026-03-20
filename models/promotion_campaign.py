from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from db import Base

class PromotionCampaign(Base):
    __tablename__ = "promotion_campaigns"

    id = Column(Integer, primary_key=True, index=True)

    market_intention_id = Column(
        Integer,
        ForeignKey("market_intentions.id"),
        nullable=False
    )

    initiator_key = Column(String, nullable=False)

    status = Column(String, default="active")  # active | paused | ended

    reach_count = Column(Integer, default=0)
    engagement_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
