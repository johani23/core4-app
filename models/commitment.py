from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from db import Base


class Commitment(Base):

    __tablename__ = "commitments"

    id = Column(Integer, primary_key=True, index=True)

    campaign_id = Column(
        Integer,
        ForeignKey("campaigns.id")
    )

    email = Column(String(255), index=True)

    commitment_price = Column(Float)

    first_name = Column(String(80))

    city = Column(String(120))

    referral_source = Column(String(64), index=True)

    timestamp = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )