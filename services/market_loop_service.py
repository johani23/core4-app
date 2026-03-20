import json
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.market_loop import (
    MarketLoopCommitment,
    SystemEvent,
    GravityState,
    PricingProposal,
)

from services.elasticity_service import (
    get_or_create_elasticity,
    elasticity_multiplier,
    open_experiment,
)

# =====================================================
# Guardrails
# =====================================================

MAX_CHANGE_24H_PCT = 8.0
MIN_CONFIDENCE = 0.75
MIN_UNIQUE_BUYERS = 20
COOLDOWN_HOURS = 0


# =====================================================
# Utility
# =====================================================

def _new_trace_id() -> str:
    return uuid.uuid4().hex


def insert_event(
    db: Session,
    market_id: str,
    event_type: str,
    strength: float,
    trace_id: str,
    payload: dict | None = None,
):
    ev = SystemEvent(
        market_id=market_id,
        event_type=event_type,
        strength=strength,
        trace_id=trace_id,
        payload_json=json.dumps(payload) if payload else None,
    )
    db.add(ev)


# =====================================================
# Gravity State
# =====================================================

def get_or_create_gravity_state(
    db: Session, market_id: str, current_price: float | None = None
) -> GravityState:

    st = db.query(GravityState).filter(GravityState.market_id == market_id).first()

    if st:
        if current_price is not None and (
            st.current_price is None or st.current_price == 100.0
        ):
            st.current_price = float(current_price)
        return st

    st = GravityState(
        market_id=market_id,
        current_price=float(current_price) if current_price else 100.0,
        gi=0.0,
        rho=0.0,
        vn=0.0,
        cc=0.0,
        mode="GREEN",
        confidence=0.5,
    )

    db.add(st)
    db.flush()
    return st


# =====================================================
# Intention Engine
# =====================================================

def evaluate_market_intention(db: Session, market_id: str) -> dict:

    now = datetime.utcnow()
    t24 = now - timedelta(hours=24)
    t7d = now - timedelta(days=7)

    q24 = db.query(MarketLoopCommitment).filter(
        MarketLoopCommitment.market_id == market_id,
        MarketLoopCommitment.created_at >= t24,
    )

    q7 = db.query(MarketLoopCommitment).filter(
        MarketLoopCommitment.market_id == market_id,
        MarketLoopCommitment.created_at >= t7d,
    )

    rows24 = q24.all()
    rows7_count = q7.count()
    rows24_count = len(rows24)

    intensity = 0.0
    w_sum = 0.0
    cred_w_sum = 0.0
    buyers = set()

    for r in rows24:
        intensity += float(r.qty) * float(r.weight)
        w_sum += float(r.weight)
        cred_w_sum += float(r.credibility_score) * float(r.weight)
        if r.buyer_id:
            buyers.add(r.buyer_id)

    credibility_avg = (cred_w_sum / w_sum) if w_sum > 0 else 0.5
    unique_buyers_24h = len(buyers)

    denom = max(rows7_count, 1)
    momentum = min(max(rows24_count / denom * 7.0, 0.0), 2.0)

    intention_score = (
        (intensity * 0.6)
        + (unique_buyers_24h * 0.3)
        + (momentum * 1.0)
    )

    return {
        "intensity": intensity,
        "credibility_avg": float(credibility_avg),
        "unique_buyers_24h": unique_buyers_24h,
        "momentum": float(momentum),
        "intention_score": float(intention_score),
    }


# =====================================================
# Gravity Mapping
# =====================================================

def evaluate_gravity_for_market(
    db: Session, market_id: str, intention: dict
) -> GravityState:

    st = get_or_create_gravity_state(db, market_id)

    gi = min(intention["intention_score"] / 50.0, 1.0) * 100.0
    rho = min(intention["momentum"] / 2.0, 1.0) * 100.0
    vn = min(intention["unique_buyers_24h"] / 200.0, 1.0) * 100.0
    cc = min(max(intention["credibility_avg"], 0.0), 1.0) * 100.0

    confidence = min(0.4 + 0.6 * intention["credibility_avg"], 1.0)

    if intention["unique_buyers_24h"] >= MIN_UNIQUE_BUYERS:
        confidence = min(confidence + 0.1, 1.0)

    if gi >= 70 and confidence >= 0.8:
        mode = "GREEN"
    elif gi >= 40:
        mode = "YELLOW"
    else:
        mode = "RED"

    st.gi = float(gi)
    st.rho = float(rho)
    st.vn = float(vn)
    st.cc = float(cc)
    st.confidence = float(confidence)
    st.mode = mode

    return st


# =====================================================
# Guardrails
# =====================================================

def _cooldown_ok(db: Session, market_id: str) -> tuple[bool, str]:

    last = (
        db.query(PricingProposal)
        .filter(PricingProposal.market_id == market_id)
        .order_by(desc(PricingProposal.created_at))
        .first()
    )

    if not last:
        return True, ""

    age = datetime.utcnow() - last.created_at.replace(tzinfo=None)

    if age < timedelta(hours=COOLDOWN_HOURS):
        return False, f"Cooldown active ({COOLDOWN_HOURS}h)."

    return True, ""


# =====================================================
# Pricing Proposal (Elasticity + Revenue Simulation)
# =====================================================

def generate_pricing_proposal(
    db: Session,
    market_id: str,
    trace_id: str,
    intention: dict,
    st: GravityState,
) -> PricingProposal:

    current_price = float(st.current_price or 100.0)

    # Base delta formula
    delta_pct = (
        0.08 * (st.gi - 50.0)
        + 0.03 * (st.rho - 50.0)
        + 0.02 * (st.cc - 50.0)
    )

    # Elasticity influence
    est = get_or_create_elasticity(db, market_id)
    mult = elasticity_multiplier(est.elasticity)
    delta_pct *= mult

    delta_pct = max(min(delta_pct, MAX_CHANGE_24H_PCT), -MAX_CHANGE_24H_PCT)

    proposed_price = current_price * (1.0 + (delta_pct / 100.0))

    # -----------------------------------------
    # Revenue Impact Simulation
    # -----------------------------------------

    elasticity = est.elasticity
    expected_units_change_pct = -elasticity * (delta_pct / 100.0)

    # clamp demand prediction
    expected_units_change_pct = max(min(expected_units_change_pct, 0.5), -0.5)

    new_revenue_index = (1 + (delta_pct / 100.0)) * (1 + expected_units_change_pct)
    expected_revenue_delta_pct = (new_revenue_index - 1.0) * 100.0

    if abs(expected_units_change_pct) < 0.05:
        risk_band = "LOW"
    elif abs(expected_units_change_pct) < 0.15:
        risk_band = "MEDIUM"
    else:
        risk_band = "HIGH"

    # -----------------------------------------
    # Guardrails
    # -----------------------------------------

    guardrail_status = "PASS"
    guardrail_reason = ""

    if st.confidence < MIN_CONFIDENCE:
        guardrail_status = "FAIL"
        guardrail_reason = "Low confidence."

    if intention["unique_buyers_24h"] < MIN_UNIQUE_BUYERS:
        guardrail_status = "FAIL"
        guardrail_reason = "Not enough unique buyers."

    ok_cd, cd_reason = _cooldown_ok(db, market_id)
    if not ok_cd:
        guardrail_status = "FAIL"
        guardrail_reason = cd_reason

    reason = (
        f"GI={st.gi:.1f}, "
        f"elasticity={elasticity:.2f}, "
        f"exp_rev_delta={expected_revenue_delta_pct:.2f}%, "
        f"risk={risk_band}"
    )

    prop = PricingProposal(
        market_id=market_id,
        current_price=current_price,
        proposed_price=float(round(proposed_price, 2)),
        delta_pct=float(round(delta_pct, 2)),
        confidence=float(round(st.confidence, 3)),
        reason=reason,
        guardrail_status=guardrail_status,
        guardrail_reason=guardrail_reason,
        status="PROPOSED",
        trace_id=trace_id,
    )

    db.add(prop)
    db.flush()
    return prop


# =====================================================
# Apply Proposal
# =====================================================

def apply_proposal(db: Session, proposal_id: int) -> PricingProposal:

    prop = db.query(PricingProposal).filter(
        PricingProposal.id == proposal_id
    ).first()

    if not prop:
        raise ValueError("Proposal not found")

    if prop.guardrail_status != "PASS":
        raise ValueError("Cannot apply proposal: guardrails failed")

    if prop.status == "APPLIED":
        return prop

    st = get_or_create_gravity_state(db, prop.market_id)
    st.current_price = float(prop.proposed_price)

    prop.status = "APPLIED"

    insert_event(
        db=db,
        market_id=prop.market_id,
        event_type="PROPOSAL_APPLIED",
        strength=abs(float(prop.delta_pct)),
        trace_id=prop.trace_id,
        payload={
            "proposal_id": prop.id,
            "new_price": prop.proposed_price,
        },
    )

    open_experiment(db, prop.market_id, prop)

    return prop
