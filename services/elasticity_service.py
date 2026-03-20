from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from models.elasticity_state import ElasticityState
from models.price_experiment import PriceExperiment


# ============================================
# Configuration
# ============================================

ALPHA = 0.25              # EWMA smoothing
WINDOW_HOURS = 6          # Observation window
MIN_DATA_ORDERS = 2       # Ignore tiny noise


# ============================================
# Elasticity State
# ============================================

def get_or_create_elasticity(db: Session, market_id: str) -> ElasticityState:
    st = (
        db.query(ElasticityState)
        .filter(ElasticityState.market_id == market_id)
        .first()
    )

    if st:
        return st

    st = ElasticityState(
        market_id=market_id,
        conv_ewma=0.0,
        elasticity=1.0,
        last_price=0.0,
    )

    db.add(st)
    db.flush()
    return st


# ============================================
# Experiment Handling
# ============================================

def open_experiment(db: Session, market_id: str, proposal) -> PriceExperiment:
    """
    Open new experiment when a proposal is applied.
    """
    exp = PriceExperiment(
        market_id=market_id,
        proposal_id=proposal.id,
        applied_price=proposal.proposed_price,
        closed=0,
    )

    db.add(exp)
    db.flush()
    return exp


def register_order_for_market(db: Session, market_id: str):
    """
    Increment orders_count for latest open experiment of this market.
    Called whenever an Order is created.
    """

    exp = (
        db.query(PriceExperiment)
        .filter(
            PriceExperiment.market_id == market_id,
            PriceExperiment.closed == 0,
        )
        .order_by(PriceExperiment.start_at.desc())
        .first()
    )

    if not exp:
        return

    exp.orders_count += 1


# ============================================
# Close Experiments & Update Elasticity
# ============================================

def close_due_experiments(db: Session):
    """
    Close experiments whose observation window passed
    and update ElasticityState accordingly.
    """

    now = datetime.utcnow()
    cutoff = now - timedelta(hours=WINDOW_HOURS)

    due_experiments = (
        db.query(PriceExperiment)
        .filter(
            PriceExperiment.closed == 0,
            PriceExperiment.start_at <= cutoff,
        )
        .all()
    )

    for exp in due_experiments:

        orders = exp.orders_count

        exp.end_at = now
        exp.closed = 1

        if orders < MIN_DATA_ORDERS:
            continue

        est = get_or_create_elasticity(db, exp.market_id)

        prev_conv = est.conv_ewma
        conv = orders / float(WINDOW_HOURS)

        # EWMA smoothing
        new_conv = (ALPHA * conv) + ((1 - ALPHA) * prev_conv)
        est.conv_ewma = new_conv

        # ----------------------------------------
        # Elasticity Adjustment Logic
        # ----------------------------------------

        price_prev = est.last_price if est.last_price > 0 else exp.applied_price
        price_now = exp.applied_price

        price_change_pct = 0.0
        if price_prev > 0:
            price_change_pct = (price_now - price_prev) / price_prev

        conv_change = new_conv - prev_conv

        elasticity = est.elasticity

        # Case 1: Price increased but demand dropped
        if price_change_pct > 0 and conv_change < 0:
            elasticity += 0.12

        # Case 2: Price increased and demand stable or rising
        elif price_change_pct > 0 and conv_change >= 0:
            elasticity -= 0.08

        # Case 3: Price decreased and demand rose
        elif price_change_pct < 0 and conv_change > 0:
            elasticity += 0.05

        # Neutral decay toward 1.0
        else:
            elasticity -= 0.02

        elasticity = max(0.5, min(elasticity, 3.0))

        est.elasticity = elasticity
        est.last_price = price_now


# ============================================
# Elasticity Multiplier
# ============================================

def elasticity_multiplier(elasticity: float) -> float:
    """
    Convert elasticity into delta modifier.
    Higher elasticity → smaller price increases.
    """

    if elasticity <= 0.7:
        return 1.10

    if elasticity <= 1.0:
        return 1.00

    if elasticity <= 1.8:
        return 0.80

    return 0.60
