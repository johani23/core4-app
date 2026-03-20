# ============================================================================
# 💠 DCT (Demand Commitment Ticket) Router — Test Harness API
# ============================================================================

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func

from db import get_db
from models.signal import Signal
from models.market_intention import MarketIntention
from models.tribe_signal import TribeSignal

from gravity.gravity import evaluate_category as gravity_evaluate


router = APIRouter(prefix="/api/dct", tags=["dct"])


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def _safe_set(obj: Any, field: str, value: Any) -> None:
    if hasattr(obj, field):
        setattr(obj, field, value)


def _safe_get(obj: Any, field: str, default: Any = None) -> Any:
    return getattr(obj, field, default)


def _now_utc() -> datetime:
    return datetime.utcnow()


def _get_user_identity(request: Request) -> Dict[str, Any]:
    uid = request.headers.get("x-user-id")
    return {"user_id": int(uid) if uid and uid.isdigit() else None}


# ----------------------------------------------------------------------------
# Request Models
# ----------------------------------------------------------------------------
class CreateSignalReq(BaseModel):
    category: str
    feature_value: str
    image_url: Optional[str] = None
    tribe_id: Optional[int] = None


class InterestReq(BaseModel):
    signal_id: int
    category: str
    tribe_id: Optional[int] = None


class AutoCampaignReq(BaseModel):
    category: str
    signal_id: int
    window_hours: int = 48
    tiers: List[Dict[str, Any]] = Field(
        default_factory=lambda: [
            {"min_buyers": 100, "discount_pct": 10},
            {"min_buyers": 200, "discount_pct": 20},
            {"min_buyers": 300, "discount_pct": 50},
        ]
    )


class BoostReq(BaseModel):
    category: str
    signal_id: int
    tribe_id: Optional[int] = None
    message: Optional[str] = "Join now to unlock the next tier."


# ----------------------------------------------------------------------------
# A1) Create Signal
# ----------------------------------------------------------------------------
@router.post("/signal")
def create_signal(payload: CreateSignalReq, request: Request, db: Session = Depends(get_db)):
    user = _get_user_identity(request)

    s = Signal()

    s.post_id = 1

    _safe_set(s, "category", payload.category)
    _safe_set(s, "image_url", payload.image_url)
    _safe_set(s, "feature_value", payload.feature_value)
    _safe_set(s, "created_at", _now_utc())
    _safe_set(s, "user_id", user["user_id"])
    _safe_set(s, "tribe_id", payload.tribe_id)

    _safe_set(s, "signal_type", "DEMAND_SIGNAL")
    _safe_set(s, "intent", "interested")
    _safe_set(s, "confidence", 0.6)

    db.add(s)
    db.commit()
    db.refresh(s)

    return {
        "ok": True,
        "signal_id": s.id
    }


# ----------------------------------------------------------------------------
# A2) Mark Interest
# ----------------------------------------------------------------------------
@router.post("/interest")
def mark_interest(payload: InterestReq, request: Request, db: Session = Depends(get_db)):
    user = _get_user_identity(request)
    user_id = user["user_id"]

    sig = db.query(Signal).filter(Signal.id == payload.signal_id).first()

    if not sig:
        return {"ok": False, "error": "Signal not found"}

    # user dedupe
    if (
        user_id is not None
        and hasattr(MarketIntention, "user_id")
        and hasattr(MarketIntention, "signal_id")
    ):
        existing = (
            db.query(MarketIntention)
            .filter(
                MarketIntention.user_id == user_id,
                MarketIntention.signal_id == payload.signal_id,
            )
            .first()
        )

        if existing:
            total_interest = _count_interest(db, payload.signal_id)
            return {"ok": True, "deduped": True, "total_interest": total_interest}

    # tribe dedupe
    existing = (
        db.query(MarketIntention)
        .filter(
            MarketIntention.signal_id == payload.signal_id,
            MarketIntention.tribe_id == payload.tribe_id
        )
        .first()
    )

    if existing:
        total_interest = _count_interest(db, payload.signal_id)
        return {"ok": True, "deduped": True, "total_interest": total_interest}

    mi = MarketIntention()

    _safe_set(mi, "feature_text", _safe_get(sig, "feature_value", ""))
    _safe_set(mi, "quantity_interest", 1)

    _safe_set(mi, "category", payload.category)
    _safe_set(mi, "created_at", _now_utc())
    _safe_set(mi, "signal_id", payload.signal_id)
    _safe_set(mi, "user_id", user_id)
    _safe_set(mi, "tribe_id", payload.tribe_id)
    _safe_set(mi, "status", "INTERESTED")

    db.add(mi)
    db.commit()

    total_interest = _count_interest(db, payload.signal_id)

    return {
        "ok": True,
        "total_interest": total_interest
    }


# ----------------------------------------------------------------------------
# Count Interest
# ----------------------------------------------------------------------------
def _count_interest(db: Session, signal_id: int) -> int:
    return int(
        db.query(func.count(MarketIntention.id))
        .filter(MarketIntention.signal_id == signal_id)
        .scalar()
        or 0
    )


# ----------------------------------------------------------------------------
# Merchant Demand List
# ----------------------------------------------------------------------------
@router.get("/demand-list")
def demand_list(category: str, db: Session = Depends(get_db)):

    sig_q = db.query(Signal)

    if hasattr(Signal, "category"):
        sig_q = sig_q.filter(Signal.category == category)

    sigs = sig_q.order_by(Signal.created_at.desc()).limit(50).all()

    g = gravity_evaluate(db, category)
    gi = float(g.get("gi", 0.0))
    mode = g.get("mode", "INCUBATION")

    items = []

    for s in sigs:

        sid = s.id
        interest = _count_interest(db, sid)

        items.append(
            {
                "signal_id": sid,
                "category": category,
                "feature_value": _safe_get(s, "feature_value", ""),
                "image_url": _safe_get(s, "image_url", None),
                "interest_count": interest,
                "gravity_index": round(gi, 4),
                "mode": mode,
            }
        )

    return {"ok": True, "items": items}


# ----------------------------------------------------------------------------
# Auto Campaign
# ----------------------------------------------------------------------------
@router.post("/auto-campaign")
def auto_campaign(payload: AutoCampaignReq, db: Session = Depends(get_db)):

    g = gravity_evaluate(db, payload.category)

    gi = float(g.get("gi", 0.0))
    mode = g.get("mode", "INCUBATION")

    interest_count = _count_interest(db, payload.signal_id)

    tiers_out = []

    for t in payload.tiers:

        tiers_out.append(
            {
                "min_buyers": int(t["min_buyers"]),
                "discount_pct": float(t["discount_pct"]),
                "status": "REACHED" if interest_count >= int(t["min_buyers"]) else "PENDING",
            }
        )

    auto_exec_prob = min(99, max(50, int(50 + gi * 50)))

    dct_id = f"intent_{payload.category}_{payload.signal_id}"

    return {
        "dct_id": dct_id,
        "status": "SUMMONS_ACTIVE" if mode == "SUMMONS" else "INCUBATION",
        "category": payload.category,
        "signal_id": payload.signal_id,
        "gravity_index": round(gi, 4),
        "interest_count": interest_count,
        "recommended_tiers": tiers_out,
        "integrity_window": f"{payload.window_hours}h",
        "auto_execution_probability": f"{auto_exec_prob}%"
    }


# ----------------------------------------------------------------------------
# Tribe Boost
# ----------------------------------------------------------------------------
@router.post("/boost")
def boost(payload: BoostReq, request: Request, db: Session = Depends(get_db)):

    user = _get_user_identity(request)

    if TribeSignal is not None:
        try:

            ts = TribeSignal()

            _safe_set(ts, "category", payload.category)
            _safe_set(ts, "signal_id", payload.signal_id)
            _safe_set(ts, "tribe_id", payload.tribe_id)
            _safe_set(ts, "created_at", _now_utc())
            _safe_set(ts, "user_id", user["user_id"])
            _safe_set(ts, "action", "BOOST")

            db.add(ts)
            db.commit()

            return {"ok": True, "boost_recorded": "TRIBE_SIGNAL"}

        except Exception:
            db.rollback()

    s = Signal()

    s.post_id = 1

    _safe_set(s, "category", payload.category)
    _safe_set(s, "created_at", _now_utc())
    _safe_set(s, "user_id", user["user_id"])
    _safe_set(s, "tribe_id", payload.tribe_id)
    _safe_set(s, "signal_type", "BOOST")
    _safe_set(s, "intent", "interested")
    _safe_set(s, "confidence", 0.6)
    _safe_set(s, "feature_value", payload.message)

    db.add(s)
    db.commit()

    return {"ok": True, "boost_recorded": "BOOST_SIGNAL"}


# ----------------------------------------------------------------------------
# Status
# ----------------------------------------------------------------------------
@router.get("/status")
def status(signal_id: int, category: str, db: Session = Depends(get_db)):

    g = gravity_evaluate(db, category)

    interest_count = _count_interest(db, signal_id)

    return {
        "ok": True,
        "signal_id": signal_id,
        "category": category,
        "interest_count": interest_count,
        "gravity": g,
    }