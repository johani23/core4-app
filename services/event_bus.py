import json
from sqlalchemy.orm import Session
from models.market_event import MarketEvent

def emit_event(
    db: Session,
    event_type: str,
    category: str,
    gi: float | None = None,
    rho: float | None = None,
    vn: float | None = None,
    cc: float | None = None,
    payload: dict | None = None,
):
    ev = MarketEvent(
        event_type=event_type,
        category=category,
        gi=gi,
        rho=rho,
        vn=vn,
        cc=cc,
        payload_json=json.dumps(payload or {}, ensure_ascii=False),
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev
