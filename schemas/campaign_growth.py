from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class JoinCampaignIn(BaseModel):

    email: EmailStr

    commitment_price: float

    first_name: Optional[str] = None

    city: Optional[str] = None

    referral_source: Optional[str] = None


class JoinCampaignOut(BaseModel):

    success: bool

    buyers_joined: int

    referral_code: str

    next_unlock_price: Optional[float]

    buyers_needed_for_next_unlock: Optional[int]


class RecentJoinItem(BaseModel):

    name: str

    city: Optional[str]

    joined_at: datetime


class RecentJoinsOut(BaseModel):

    buyers_joined_today: int

    buyers_joined_last_hour: int

    items: List[RecentJoinItem]


class ReferralStatsOut(BaseModel):

    friends_joined: int

    total_contribution: int