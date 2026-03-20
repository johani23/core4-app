from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Summons
from ..security import decode_token

router = APIRouter(prefix="/merchant", tags=["merchant"])

def require_merchant(request: Request):
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "Missing token")
    payload = decode_token(auth.split(" ",1)[1])
    if payload.get("role") != "merchant":
        raise HTTPException(403, "Forbidden")
    return int(payload["sub"])

@router.get("/summons")
def my_summons(request: Request, db: Session = Depends(get_db)):
    mid = require_merchant(request)
    items = db.query(Summons).filter(Summons.merchant_id==mid).order_by(Summons.created_at.desc()).limit(50).all()
    return [{
        "id": s.id,
        "category": s.category,
        "market_size_units": s.market_size_units,
        "fixed_price_point": s.fixed_price_point,
        "conversion_probability": s.conversion_probability,
        "leakage_risk": s.leakage_risk,
        "window_hours": s.window_hours,
        "status": s.status,
        "created_at": s.created_at.isoformat()
    } for s in items]

@router.post("/summons/{summons_id}/accept")
def accept(summons_id: int, request: Request, db: Session = Depends(get_db)):
    mid = require_merchant(request)
    s = db.query(Summons).filter(Summons.id==summons_id, Summons.merchant_id==mid).first()
    if not s:
        raise HTTPException(404, "Not found")
    s.status = "ACCEPTED"
    db.add(s); db.commit()
    return {"ok": True}
