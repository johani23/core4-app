# ============================================================================
# 💠 Gravity API Router
# ============================================================================
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import get_db
from gravity.gravity import evaluate_category

router = APIRouter(
    prefix="/api/gravity",
    tags=["gravity"],
)

@router.post("/evaluate/{category}")
def evaluate(category: str, db: Session = Depends(get_db)):
    state = evaluate_category(db, category)
    return {
        "category": state.category,
        "gi": state.gi,
        "rho": state.rho,
        "vn": state.vn,
        "cc": state.cc,
        "mode": state.mode,
    }
# ============================================================================
# 🔹 Post-level Gravity Snapshot (Demand Signals)
# Minimal • Engine-only • No UI
# ============================================================================

from datetime import datetime, timedelta, timezone
from sqlalchemy import and_
from models.signal import Signal

WINDOW_MINUTES = 30
QUALIFIED_AT = 10
HOT_AT = 25


def _status_from_count(count: int) -> str:
    if count >= HOT_AT:
        return "hot"
    if count >= QUALIFIED_AT:
        return "qualified"
    if count >= 5:
        return "warming"
    return "cold"


@router.get("/snapshot/post/{post_id}")
def gravity_snapshot_post(post_id: str, db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(minutes=WINDOW_MINUTES)

    # Total interested signals
    total = (
        db.query(Signal)
        .filter(
            and_(
                Signal.post_id == post_id,
                Signal.signal_type == "demand",
                Signal.intent == "interested",
            )
        )
        .count()
    )

    # Velocity (count in window)
    rows = (
        db.query(Signal.created_at)
        .filter(
            and_(
                Signal.post_id == post_id,
                Signal.signal_type == "demand",
                Signal.intent == "interested",
            )
        )
        .all()
    )

    ts_list = []
    for (ts,) in rows:
        if ts is None:
            continue
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        ts_list.append(ts)

    window_count = len([t for t in ts_list if t >= window_start])
    velocity_per_min = window_count / float(WINDOW_MINUTES)

    return {
        "post_id": post_id,
        "interest_count": total,
        "window_minutes": WINDOW_MINUTES,
        "window_count": window_count,
        "velocity_per_min": round(velocity_per_min, 4),
        "status": _status_from_count(total),
        "qualified": total >= QUALIFIED_AT,
        "ts_utc": now.isoformat(),
    }
