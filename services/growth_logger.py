# ====================================================================
# 🚀 Core4.AI – Growth Logger Service (FINAL – SAFE & COMPLETE)
# ====================================================================

from sqlalchemy.orm import Session
from models.growth_event import GrowthEvent


def log_event(
    db: Session,
    event_type: str,
    user_id: int = None,
    campaign_id: int = None,
    ref_code: str = None,
    metadata: dict = None,
):
    event = GrowthEvent(
        user_id=user_id,
        campaign_id=campaign_id,   # ✅ added
        ref_code=ref_code,         # ✅ added
        event_type=event_type,
        event_metadata=metadata or {},
    )

    # IMPORTANT:
    # add only — router owns commit
    db.add(event)

    return event