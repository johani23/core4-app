# routers/market_loop_router.py

import json
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

from db import get_db
from schemas.market_loop import CommitRequest, MarketStateOut
from models.market_loop import MarketLoopCommitment, PricingProposal, SystemEvent
from services.market_loop_service import (
    _new_trace_id,
    insert_event,
    get_or_create_gravity_state,
    evaluate_market_intention,
    evaluate_gravity_for_market,
    generate_pricing_proposal,
    apply_proposal,
)
from services.elasticity_service import get_or_create_elasticity


router = APIRouter(prefix="/api/market", tags=["market-loop"])


# =====================================================
# CREATE COMMIT
# =====================================================

@router.post("/commit")
def create_commit(req: CommitRequest, db: Session = Depends(get_db)):
    trace_id = _new_trace_id()

    # Insert commitment
    c = MarketLoopCommitment(
        market_id=req.market_id,
        buyer_id=req.buyer_id,
        qty=req.qty,
        intent_type=req.intent_type,
        weight=req.weight,
        credibility_score=req.credibility_score,
        price_ceiling=req.price_ceiling,
    )
    db.add(c)

    insert_event(
        db=db,
        market_id=req.market_id,
        event_type="COMMITMENT_CREATED",
        strength=float(req.qty) * float(req.weight),
        trace_id=trace_id,
        payload={"buyer_id": req.buyer_id, "qty": req.qty},
    )

    # Gravity
    st = get_or_create_gravity_state(db, req.market_id, current_price=req.current_price)
    intention = evaluate_market_intention(db, req.market_id)
    st = evaluate_gravity_for_market(db, req.market_id, intention)

    insert_event(
        db=db,
        market_id=req.market_id,
        event_type="INTENTION_EVALUATED",
        strength=float(intention["intention_score"]),
        trace_id=trace_id,
        payload=intention,
    )

    # Generate proposal
    prop = generate_pricing_proposal(db, req.market_id, trace_id, intention, st)

    insert_event(
        db=db,
        market_id=req.market_id,
        event_type="PROPOSAL_CREATED",
        strength=abs(float(prop.delta_pct)),
        trace_id=trace_id,
        payload={"proposal_id": prop.id},
    )

    db.commit()

    # ---------------------------------------------------------
    # 🔥 DECISION PAYLOAD
    # ---------------------------------------------------------

    est = get_or_create_elasticity(db, req.market_id)
    elasticity = est.elasticity

    expected_units_change_pct = - elasticity * (prop.delta_pct / 100.0)
    expected_units_change_pct = max(min(expected_units_change_pct, 0.5), -0.5)

    new_revenue_index = (1 + (prop.delta_pct / 100.0)) * (1 + expected_units_change_pct)
    expected_revenue_delta_pct = (new_revenue_index - 1.0) * 100.0

    if abs(expected_units_change_pct) < 0.05:
        risk_band = "LOW"
    elif abs(expected_units_change_pct) < 0.15:
        risk_band = "MEDIUM"
    else:
        risk_band = "HIGH"

    return {
        "trace_id": trace_id,
        "gravity": {
            "market_id": st.market_id,
            "gi": st.gi,
            "rho": st.rho,
            "vn": st.vn,
            "cc": st.cc,
            "mode": st.mode,
            "confidence": st.confidence,
            "current_price": st.current_price,
        },
        "proposal": {
            "id": prop.id,
            "market_id": prop.market_id,
            "current_price": prop.current_price,
            "proposed_price": prop.proposed_price,
            "delta_pct": prop.delta_pct,
            "confidence": prop.confidence,
            "elasticity": round(elasticity, 3),
            "expected_units_change_pct": round(expected_units_change_pct * 100, 2),
            "expected_revenue_delta_pct": round(expected_revenue_delta_pct, 2),
            "risk_band": risk_band,
            "reason": prop.reason,
            "guardrail_status": prop.guardrail_status,
            "guardrail_reason": prop.guardrail_reason,
            "status": prop.status,
            "trace_id": prop.trace_id,
        },
    }


# =====================================================
# GET MARKET STATE
# =====================================================

@router.get("/state/{market_id}", response_model=MarketStateOut)
def get_market_state(market_id: str, db: Session = Depends(get_db)):
    st = get_or_create_gravity_state(db, market_id)

    latest_prop = (
        db.query(PricingProposal)
        .filter(PricingProposal.market_id == market_id)
        .order_by(PricingProposal.created_at.desc())
        .first()
    )

    evs = (
        db.query(SystemEvent)
        .filter(SystemEvent.market_id == market_id)
        .order_by(SystemEvent.created_at.desc())
        .limit(10)
        .all()
    )

    def parse_payload(e: SystemEvent):
        if not e.payload_json:
            return None
        try:
            return json.loads(e.payload_json)
        except Exception:
            return None

    est = get_or_create_elasticity(db, market_id)

    return {
        "gravity": {
            "market_id": st.market_id,
            "gi": st.gi,
            "rho": st.rho,
            "vn": st.vn,
            "cc": st.cc,
            "mode": st.mode,
            "confidence": st.confidence,
            "current_price": st.current_price,
        },
        "latest_proposal": None if not latest_prop else {
            "id": latest_prop.id,
            "market_id": latest_prop.market_id,
            "current_price": latest_prop.current_price,
            "proposed_price": latest_prop.proposed_price,
            "delta_pct": latest_prop.delta_pct,
            "confidence": latest_prop.confidence,
            "elasticity": round(est.elasticity, 3),
            "expected_units_change_pct": 0.0,
            "expected_revenue_delta_pct": 0.0,
            "risk_band": "N/A",
            "reason": latest_prop.reason,
            "guardrail_status": latest_prop.guardrail_status,
            "guardrail_reason": latest_prop.guardrail_reason,
            "status": latest_prop.status,
            "trace_id": latest_prop.trace_id,
        },
        "recent_events": [
            {
                "event_type": e.event_type,
                "strength": e.strength,
                "trace_id": e.trace_id,
                "payload": parse_payload(e),
            }
            for e in evs
        ],
    }


# =====================================================
# APPLY PROPOSAL
# =====================================================

pricing_router = APIRouter(prefix="/api/pricing", tags=["pricing-loop"])


@pricing_router.post("/apply/{proposal_id}")
def apply(proposal_id: int, db: Session = Depends(get_db)):
    try:
        prop = apply_proposal(db, proposal_id)
        db.commit()
        return {
            "ok": True,
            "proposal_id": prop.id,
            "status": prop.status,
            "new_price": prop.proposed_price,
        }
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
