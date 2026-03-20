from fastapi import APIRouter, Depends
from datetime import datetime

router = APIRouter(
    prefix="/api/admin/market-health",
    tags=["Admin Market Health"],
)

# NOTE:
# لاحقًا يمكن ربطها بقاعدة بيانات
# الآن نقرأ آخر Early Warning Signal في الذاكرة / log

# MOCK STATE (مؤقت للـ Beta)
LATEST_MARKET_STATE = {
    "status": "GREEN",
    "avg_trust": 0.42,
    "recent_sales": 18,
    "interventions": 2,
    "eta": "STABLE",
    "updated_at": datetime.utcnow(),
}

@router.get("/")
def get_market_health():
    return {
        "status": LATEST_MARKET_STATE["status"],
        "avg_trust": LATEST_MARKET_STATE["avg_trust"],
        "recent_sales": LATEST_MARKET_STATE["recent_sales"],
        "interventions": LATEST_MARKET_STATE["interventions"],
        "eta": LATEST_MARKET_STATE["eta"],
        "updated_at": LATEST_MARKET_STATE["updated_at"],
    }
