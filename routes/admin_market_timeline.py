from fastapi import APIRouter, Depends
from routes.admin_guard import admin_guard
from routes.system_early_warning import EARLY_WARNING_HISTORY

router = APIRouter(
    prefix="/api/admin/market-timeline",
    tags=["Admin Market Timeline"],
)

@router.get("/", dependencies=[Depends(admin_guard)])
def get_market_timeline():
    """
    Returns chronological Early Warning history
    (latest first).
    """
    return list(EARLY_WARNING_HISTORY)
