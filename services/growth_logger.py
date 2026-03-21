# ====================================================================
# 🚀 Core4.AI – Growth Logger Service (FIXED)
# ====================================================================

from sqlalchemy.orm import Session
from models.growth_event import GrowthEvent


def log_event(
    db: Session,
    event_type: str,
    user_id: int = None,
    metadata: dict = None
):
    event = GrowthEvent(
        user_id=user_id,
        event_type=event_type,
        event_metadata=metadata or {}   # ✅ FIXED
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event