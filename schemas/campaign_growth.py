# ====================================================================
# 💚 Core4.AI – Campaign Growth Schemas (FINAL PRODUCTION LOCKED)
# ====================================================================

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# =========================================================
# JOIN INPUT (STRICT & SAFE)
# =========================================================

class JoinCampaignIn(BaseModel):

    email: EmailStr = Field(
        ...,
        description="User email (unique per campaign)"
    )

    first_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Optional first name"
    )

    city: Optional[str] = Field(
        None,
        max_length=100,
        description="Optional city"
    )

    ref_code: Optional[str] = Field(
        None,
        description="Referral code used when joining"
    )


# =========================================================
# JOIN RESPONSE (LOCKED CONTRACT)
# =========================================================

class JoinCampaignOut(BaseModel):

    success: bool = Field(..., description="Join operation success")

    buyers_joined: int = Field(..., description="Total buyers in campaign")

    referral_code: str = Field(..., description="Generated referral code")

    next_unlock_price: Optional[float] = Field(
        None,
        description="Next price to unlock"
    )

    buyers_needed_for_next_unlock: Optional[int] = Field(
        None,
        description="Remaining buyers needed to unlock next price"
    )


# =========================================================
# RECENT JOINS
# =========================================================

class RecentJoinItem(BaseModel):

    first_name: Optional[str] = Field(None, description="First name")

    city: Optional[str] = Field(None, description="City")

    joined_at: datetime = Field(..., description="Join timestamp")

    class Config:
        orm_mode = True


class RecentJoinsOut(BaseModel):

    buyers_joined_today: int = Field(
        ...,
        description="Number of buyers joined today"
    )

    buyers_joined_last_hour: int = Field(
        ...,
        description="Number of buyers joined in the last hour"
    )

    items: List[RecentJoinItem] = Field(
        ...,
        description="List of recent joins"
    )


# =========================================================
# REFERRAL STATS
# =========================================================

class ReferralStatsOut(BaseModel):

    ref_code: str = Field(..., description="Referral code")

    invite_link: str = Field(..., description="Generated invite link")

    friends_joined: int = Field(
        ...,
        description="Number of users who joined using this referral"
    )


# =========================================================
# MOMENTUM (PRODUCTION READY)
# =========================================================

class CampaignMomentumOut(BaseModel):

    campaign_id: int = Field(..., description="Campaign ID")

    buyers_joined: int = Field(..., description="Total buyers joined")

    recent_joins_24h: int = Field(
        ...,
        description="Buyers joined in last 24 hours"
    )

    buyers_needed_for_next_unlock: Optional[int] = Field(
        None,
        description="Remaining buyers for next unlock"
    )

    next_unlock_price: Optional[float] = Field(
        None,
        description="Next unlock price"
    )

    is_trending: bool = Field(
        ...,
        description="Whether campaign is trending"
    )

    is_near_unlock: bool = Field(
        ...,
        description="Whether campaign is close to next unlock"
    )