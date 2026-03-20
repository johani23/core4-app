# ====================================================================
# 🚀 Core4.AI – Growth Logger Service
# Centralized event tracking for growth loop
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
        metadata=metadata or {}
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event