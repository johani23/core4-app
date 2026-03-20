from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from services.elasticity_service import close_due_experiments

router = APIRouter(prefix="/api/elasticity", tags=["elasticity"])

@router.post("/close-due")
def close_due(db: Session = Depends(get_db)):
    close_due_experiments(db)
    db.commit()
    return {"ok": True}
