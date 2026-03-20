# ============================================================================
# 🧠 Market Intelligence Engine (Core4.AI – Demand + Supply)
# Works on MarketLoopCommitment + MarketBracket + Gravity + MerchantCommitment
# ============================================================================

from sqlalchemy.orm import Session
from sqlalchemy import func

from models.market_loop import MarketLoopCommitment
from commitment.market_brackets import MarketBracket
from commitment.system_events import SystemEvent

from models.merchant_commitment import MerchantCommitment
from gravity.gravity import evaluate_category


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def _vn_to_velocity(vn: float) -> str:
    if vn < 0.35:
        return "LOW"
    if vn > 0.65:
        return "HIGH"
    return "MED"


def _estimate_unlock_prob(gi: float, next_progress: float, velocity: str) -> float:
    v_weight = {"LOW": 0.2, "MED": 0.5, "HIGH": 0.8}.get(velocity, 0.5)
    return _clamp((0.5 * gi) + (0.4 * next_progress) + (0.1 * v_weight))


def _already_emitted(db: Session, market_intention_id: int, bracket_id: int) -> bool:
    events = db.query(SystemEvent).filter(
        SystemEvent.event_type == "MARKET_BRACKET_UNLOCKED"
    ).all()

    for e in events:
        payload = e.payload or {}
        if (
            payload.get("market_intention_id") == market_intention_id
            and payload.get("bracket_id") == bracket_id
        ):
            return True

    return False


def _supply_summary(db: Session, market_intention_id: int):
    ready_rows = (
        db.query(MerchantCommitment)
        .filter(
            MerchantCommitment.market_intention_id == market_intention_id,
            MerchantCommitment.status == "ready",
        )
        .all()
    )

    merchants_ready = len(ready_rows)
    total_capacity = sum(int(r.capacity or 0) for r in ready_rows) if ready_rows else 0

    mins = [float(r.confirmed_min_price) for r in ready_rows if r.confirmed_min_price is not None]
    maxs = [float(r.confirmed_max_price) for r in ready_rows if r.confirmed_max_price is not None]

    supply_price_floor = min(mins) if mins else None
    supply_price_ceiling = max(maxs) if maxs else None

    return {
        "merchants_ready": merchants_ready,
        "total_capacity": total_capacity,
        "supply_price_floor": supply_price_floor,
        "supply_price_ceiling": supply_price_ceiling,
    }


def _decide_action(
    gi: float,
    mode: str,
    unlock_prob: float,
    merchants_ready: int,
    total_capacity: int,
) -> str:

    mode = (mode or "").upper()

    # Strong demand but no supply → recruit merchants
    if mode == "SUMMONS" and merchants_ready == 0:
        return "PUSH"

    # Strong demand and supply exists → stabilize
    if mode == "SUMMONS" and merchants_ready > 0:
        return "HOLD"

    # Weak demand
    if gi < 0.20:
        if merchants_ready > 0:
            return "WAIT"
        return "BOOST"

    # Near unlock
    if unlock_prob >= 0.75 and gi >= 0.50:
        if merchants_ready > 0 and total_capacity > 0:
            return "HOLD"
        return "PUSH"

    # Mid demand
    if gi >= 0.35:
        if merchants_ready == 0:
            return "PUSH"
        return "BOOST"

    return "HOLD"


# ---------------------------------------------------------------------------
# PUBLIC ENTRY POINT
# ---------------------------------------------------------------------------

def evaluate_market_intelligence(
    db: Session,
    market_intention_id: int,
    category: str,
):

    # -----------------------------------------------------------------------
    # 1) Demand Commitments
    # -----------------------------------------------------------------------

    total_commitments = (
        db.query(func.coalesce(func.sum(MarketLoopCommitment.quantity), 0))
        .filter(
            MarketLoopCommitment.market_intention_id == market_intention_id,
            MarketLoopCommitment.is_active == True,  # noqa
        )
        .scalar()
        or 0
    )

    total_commitments = int(total_commitments)

    # -----------------------------------------------------------------------
    # 2) Brackets
    # -----------------------------------------------------------------------

    brackets = (
        db.query(MarketBracket)
        .filter(
            MarketBracket.market_intention_id == market_intention_id,
            MarketBracket.is_active == True,  # noqa
        )
        .order_by(MarketBracket.rank.asc())
        .all()
    )

    bracket_states = []
    active_bracket_id = None
    next_bracket_id = None

    for b in brackets:
        required = int(b.required_commitments)
        unlocked = total_commitments >= required

        if unlocked:
            active_bracket_id = b.id
        elif next_bracket_id is None:
            next_bracket_id = b.id

        progress = 1.0 if required == 0 else min(1.0, total_commitments / required)
        remaining = max(0, required - total_commitments)

        bracket_states.append({
            "id": b.id,
            "name": getattr(b, "name", f"Bracket {b.rank}"),
            "rank": int(b.rank),
            "required_commitments": required,
            "unlocked": unlocked,
            "progress": round(progress, 4),
            "remaining": remaining,
        })

    # -----------------------------------------------------------------------
    # 3) Gravity
    # -----------------------------------------------------------------------

    gravity_state = evaluate_category(db, category)

    gi = float(gravity_state["gi"])
    rho = float(gravity_state["rho"])
    vn = float(gravity_state["vn"])
    cc = float(gravity_state["cc"])
    mode = gravity_state["mode"]

    velocity = _vn_to_velocity(vn)

    # -----------------------------------------------------------------------
    # 4) Supply
    # -----------------------------------------------------------------------

    supply = _supply_summary(db, market_intention_id)

    # -----------------------------------------------------------------------
    # 5) Decision
    # -----------------------------------------------------------------------

    next_progress = 0.0
    if next_bracket_id:
        next_bracket = next(
            b for b in bracket_states if b["id"] == next_bracket_id
        )
        next_progress = next_bracket["progress"]

    unlock_probability = _estimate_unlock_prob(gi, next_progress, velocity)

    action = _decide_action(
        gi,
        mode,
        unlock_probability,
        merchants_ready=supply["merchants_ready"],
        total_capacity=supply["total_capacity"],
    )

    confidence = _clamp((0.65 * gi) + (0.35 * unlock_probability))

    # -----------------------------------------------------------------------
    # 6) Emit Unlock Events (deduped)
    # -----------------------------------------------------------------------

    emitted = []

    for b in brackets:
        if total_commitments >= int(b.required_commitments):
            if not _already_emitted(db, market_intention_id, b.id):

                event = SystemEvent(
                    event_type="MARKET_BRACKET_UNLOCKED",
                    payload={
                        "market_intention_id": market_intention_id,
                        "bracket_id": b.id,
                        "required_commitments": int(b.required_commitments),
                        "actual_commitments": total_commitments,
                    }
                )

                db.add(event)
                emitted.append(f"MARKET_BRACKET_UNLOCKED:{b.id}")

    if emitted:
        db.commit()

    # -----------------------------------------------------------------------
    # Final Output
    # -----------------------------------------------------------------------

    return {
        "market_intention_id": market_intention_id,
        "commitments_total": total_commitments,
        "active_bracket_id": active_bracket_id,
        "next_bracket_id": next_bracket_id,
        "brackets": bracket_states,
        "gravity": {
            "category": category,
            "gi": gi,
            "rho": rho,
            "vn": vn,
            "cc": cc,
            "mode": mode,
            "velocity": velocity,
        },
        "supply": supply,
        "decision": {
            "recommended_action": action,
            "unlock_probability_48h": round(unlock_probability, 4),
            "confidence": round(confidence, 4),
        },
        "emitted_events": emitted,
        "engine_version": "mie-v1",
    }
