# ====================================================================
# 📦 Core4.AI – Commitment Schemas (PRODUCTION READY)
# ====================================================================

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# =========================================================
# BRACKET CREATE
# =========================================================

class BracketCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    required_commitments: int = Field(ge=1)

    # 🔥 allow nullable (DB supports it)
    discount_percent: Optional[float] = Field(default=None, gt=0, le=95)

    price: float = Field(gt=0)

    rank: int = Field(default=0, ge=0)


# =========================================================
# OFFER CREATE
# =========================================================

class OfferCreate(BaseModel):
    merchant_id: str = Field(min_length=1, max_length=64)

    campaign_id: int

    title: str = Field(min_length=1, max_length=200)

    sku: Optional[str] = Field(default=None, max_length=80)

    currency: str = Field(default="SAR", min_length=1, max_length=8)

    base_price: float = Field(gt=0)

    brackets: List[BracketCreate]


# =========================================================
# OFFER OUT
# =========================================================

class OfferOut(BaseModel):
    id: int
    merchant_id: str
    title: str
    sku: Optional[str]
    currency: str
    base_price: float
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# =========================================================
# COMMITMENT UPSERT
# =========================================================

class CommitmentUpsert(BaseModel):
    buyer_id: str = Field(min_length=1, max_length=64)

    quantity: int = Field(default=1, ge=1, le=1000)

    commitment_type: str = Field(
        default="SOFT",
        pattern="^(SOFT|HARD)$"
    )


# =========================================================
# COMMITMENT OUT
# =========================================================

class CommitmentOut(BaseModel):
    id: int
    offer_id: int
    buyer_id: str
    quantity: int
    commitment_type: str
    is_active: bool
    weight: float
    created_at: datetime

    class Config:
        from_attributes = True


# =========================================================
# BRACKET STATE
# =========================================================

class BracketState(BaseModel):
    id: int
    name: str
    required_commitments: int

    # 🔥 must match DB + service
    discount_percent: Optional[float]

    rank: int
    unlocked: bool


# =========================================================
# ENGINE STATE
# =========================================================

class EngineState(BaseModel):
    offer_id: int
    commitments_count: int
    active_bracket: Optional[int]
    brackets: List[BracketState]
    current_price: float