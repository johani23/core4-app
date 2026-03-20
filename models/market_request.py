# ====================================================================
# 💚 Core4.AI – Market Request (Wishlist / DCT-lite)
# ====================================================================

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from db import Base


class MarketRequest(Base):
    __tablename__ = "market_requests"

    id = Column(Integer, primary_key=True, index=True)

    query = Column(String(255), nullable=False)
    email = Column(String(120), nullable=True)

    # linked once a campaign is created from this demand
    campaign_id = Column(Integer, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )