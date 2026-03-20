from fastapi import APIRouter
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(
    prefix="/api/system",
    tags=["System Signals"]
)

class EarlyWarningSignal(BaseModel):
    timestamp: datetime
    status: str           # GREEN | YELLOW | RED
    avg_trust: float
    recent_sales: int
    step: int
    interventions_triggered: bool
    context: dict | None = None


@router.post("/early-warning")
def receive_early_warning(signal: EarlyWarningSignal):
    """
    Internal system signal.
    Used for monitoring, dashboards, and governance logic.
    """
    # لاحقًا:
    # - حفظ في DB
    # - إرسال Webhook
    # - ربط Notification داخلي

    return {
        "ack": True,
        "received_at": datetime.utcnow(),
        "status": signal.status,
    }
