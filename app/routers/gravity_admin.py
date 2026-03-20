from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import GravityConfig
from ..schemas import GravityConfigUpsert
from ..security import decode_token
from ..gravity import evaluate_category

router = APIRouter(prefix="/gravity-admin", tags=["gravity-admin"])

def require_admin(request: Request):
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "Missing token")
    payload = decode_token(auth.split(" ",1)[1])
    if payload.get("role") != "admin":
        raise HTTPException(403, "Forbidden")
    return payload

@router.post("/config")
def upsert_config(payload: GravityConfigUpsert, request: Request, db: Session = Depends(get_db)):
    require_admin(request)
    cfg = db.query(GravityConfig).filter(GravityConfig.category==payload.category).first()
    if not cfg:
        cfg = GravityConfig(category=payload.category)
    cfg.gt_threshold = payload.gt_threshold
    cfg.w_rho = payload.w_rho
    cfg.w_vn = payload.w_vn
    cfg.w_cc = payload.w_cc
    db.add(cfg); db.commit()
    return {"ok": True}

@router.post("/evaluate/{category}")
def evaluate(category: str, request: Request, db: Session = Depends(get_db)):
    require_admin(request)
    st = evaluate_category(db, category)
    return {"category": st.category, "gi": st.gi, "rho": st.rho, "vn": st.vn, "cc": st.cc, "mode": st.mode}
