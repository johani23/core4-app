from sqlalchemy.orm import Session
from datetime import datetime

from models.market_event import MarketEvent
from auto_market.engine import create_auto_campaign


def process_gravity_spike_events(db: Session):

    events = (
        db.query(MarketEvent)
        .filter(
            MarketEvent.event_type == "GRAVITY_SPIKE",
            MarketEvent.processed == False
        )
        .order_by(MarketEvent.created_at.asc())
        .limit(10)
        .all()
    )

    results = []

    for ev in events:

        category = ev.category

        offer = create_auto_campaign(db, category)

        ev.processed = True
        ev.processed_at = datetime.utcnow()

        if offer:
            ev.process_notes = f"campaign_created:{offer.id}"
        else:
            ev.process_notes = "campaign_skipped_existing"

        db.add(ev)
        db.commit()

        results.append({
            "event_id": ev.id,
            "category": category,
            "campaign_created": offer.id if offer else None
        })

    return results