from pydantic import BaseModel, Field
from typing import Optional, List, Dict


# =====================================================
# Commit Request
# =====================================================

class CommitRequest(BaseModel):
    market_id: str
    buyer_id: Optional[str] = None
    qty: int = 1
    intent_type: str = "buy"
    weight: float = Field(default=1.0, ge=0.0, le=1.0)
    credibility_score: float = Field(default=0.7, ge=0.0, le=1.0)
    price_ceiling: Optional[float] = None
    current_price: Optional[float] = None


# =====================================================
# Gravity Output
# =====================================================

class GravityOut(BaseModel):
    market_id: str
    gi: float
    rho: float
    vn: float
    cc: float
    mode: str
    confidence: float
    current_price: float


# =====================================================
# 🔥 Proposal Output (Decision Payload)
# =====================================================

class ProposalOut(BaseModel):
    id: int
    market_id: str

    current_price: float
    proposed_price: float
    delta_pct: float

    confidence: float

    # 🔥 NEW — Decision Intelligence Fields
    elasticity: float
    expected_units_change_pct: float
    expected_revenue_delta_pct: float
    risk_band: str

    reason: str

    guardrail_status: str
    guardrail_reason: str

    status: str
    trace_id: str


# =====================================================
# Events
# =====================================================

class EventOut(BaseModel):
    event_type: str
    strength: float
    trace_id: str
    payload: Optional[Dict] = None


# =====================================================
# Market State
# =====================================================

class MarketStateOut(BaseModel):
    gravity: GravityOut
    latest_proposal: Optional[ProposalOut] = None
    recent_events: List[EventOut] = []
