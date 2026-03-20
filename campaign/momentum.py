# ============================================================================
# Core4.AI – Campaign Momentum Signals
# ============================================================================

from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from commitment.models import Commitment


def compute_campaign_momentum(db: Session, offer_id: int):

    now = datetime.utcnow()

    one_hour_ago = now - timedelta(hours=1)
    one_day_ago = now - timedelta(hours=24)

    # buyers last hour
    buyers_last_hour = db.query(Commitment).filter(
        Commitment.offer_id == offer_id,
        Commitment.created_at >= one_hour_ago
    ).count()

    # buyers last 24 hours
    buyers_last_day = db.query(Commitment).filter(
        Commitment.offer_id == offer_id,
        Commitment.created_at >= one_day_ago
    ).count()

    momentum_level = "slow"

    if buyers_last_hour >= 20:
        momentum_level = "hot"
    elif buyers_last_hour >= 5:
        momentum_level = "rising"

    return {
        "buyers_last_hour": buyers_last_hour,
        "buyers_last_day": buyers_last_day,
        "momentum_level": momentum_level
    }