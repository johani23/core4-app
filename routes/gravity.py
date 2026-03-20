# ============================================================================
# 💠 Gravity API Router
# ============================================================================
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import get_db
from gravity.gravity import evaluate_category

router = APIRouter(
    prefix="/api/gravity",
    tags=["gravity"],
)

@router.post("/evaluate/{category}")
def evaluate(category: str, db: Session = Depends(get_db)):
    state = evaluate_category(db, category)
    return {
        "category": state.category,
        "gi": state.gi,
        "rho": state.rho,
        "vn": state.vn,
        "cc": state.cc,
        "mode": state.mode,
    }
