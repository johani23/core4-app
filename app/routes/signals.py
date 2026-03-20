# ============================================================================
# 💚 Core4.AI — Signals Route (Pilot)
# Purpose:
# - Receive behavioral signals
# - Extract normalized signals
# - Run governance evaluation
# - Return decision (no enforcement here)
# ============================================================================
# IMPORTANT:
# - No business logic
# - No hard blocking
# - No UI assumptions
# ============================================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from db import get_db
from models.signal import Signal

# Signal + Governance engines
from app.engines.signals.signal_engine import extract_signals
from app.engines.governance.governance_executor import evaluate as evaluate_governance

router = APIRouter(
    prefix="/signals",
    tags=["Signals (Pilot)"]
)

# ---------------------------------------------------------------------------
# POST /api/signals
# ---------------------------------------------------------------------------
@router.post("/")
def ingest_signal(payload: dict, db: Session = Depends(get_db)):
    """
    Expected payload (flexible during Pilot):
    {
        "user_id": "U-123",
        "event_type": "purchase | click | silence | retry",
        "context": { ... },
        "events": [ ... ],              # recent events
        "baseline": { ... },            # user baseline
        "outcomes": [ ... ],            # past outcomes
        "regret_score": 0.7,
        "prior_intensity": 0.8,
        "silence_duration_hours": 96
    }
    """

    user_id = payload.get("user_id")
    if not user_id:
        return {"error": "user_id is required"}

    # -----------------------------------------------------------------------
    # 1️⃣ Persist raw signal (audit-first)
    # -----------------------------------------------------------------------
    raw_signal = Signal(
        user_id=user_id,
        event_type=payload.get("event_type", "unknown"),
        payload=payload,
        created_at=datetime.utcnow()
    )
    db.add(raw_signal)
    db.commit()

    # -----------------------------------------------------------------------
    # 2️⃣ Extract normalized signals
    # -----------------------------------------------------------------------
    signals = extract_signals(payload)

    # -----------------------------------------------------------------------
    # 3️⃣ Evaluate governance rules
    # -----------------------------------------------------------------------
    decision = evaluate_governance(signals, user_id)

    # -----------------------------------------------------------------------
    # 4️⃣ Lightweight decision logging (Pilot)
    # -----------------------------------------------------------------------
    decision_log = {
        "user_id": user_id,
        "signals": signals,
        "decision": decision,
        "timestamp": datetime.utcnow().isoformat()
    }

    # NOTE:
    # In Phase 1 we just return it.
    # In Phase 2 → DB table / Kafka / S3 / Audit store.

    # -----------------------------------------------------------------------
    # 5️⃣ Response (NO enforcement here)
    # -----------------------------------------------------------------------
    return {
        "status": "signal_received",
        "signals_extracted": signals,
        "governance_decision": decision,
        "pilot_note": "No action enforced. Decision returned for observation."
    }
