import time
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from db import SessionLocal
from models.market_event import MarketEvent
from services.gravity_rules import decide_pricing_action
from services.pricing_engine import apply_pricing_action

POLL_SECONDS = 1.5
BATCH_SIZE = 25

def process_once(db: Session):
    events = (
        db.query(MarketEvent)
        .filter(MarketEvent.processed == False)  # noqa
        .order_by(MarketEvent.created_at.asc())
        .limit(BATCH_SIZE)
        .all()
    )

    for ev in events:
        action_type, delta_pct, reason = decide_pricing_action(
            ev.event_type, ev.gi, ev.rho, ev.cc
        )

        if action_type and delta_pct is not None:
            action = apply_pricing_action(
                db=db,
                category=ev.category,
                action_type=action_type,
                delta_pct=delta_pct,
                event_id=ev.id,
                reason=reason,
            )
            ev.processed = True
            ev.processed_at = func.now()
            ev.process_notes = f"Applied {action_type} ({delta_pct*100:.1f}%). action_id={action.id}"
        else:
            ev.processed = True
            ev.processed_at = func.now()
            ev.process_notes = f"No-op: {reason}"

        db.commit()

def run_forever():
    while True:
        db = SessionLocal()
        try:
            process_once(db)
        finally:
            db.close()
        time.sleep(POLL_SECONDS)

if __name__ == "__main__":
    run_forever()
