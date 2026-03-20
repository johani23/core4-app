from fastapi import APIRouter
from datetime import datetime
from pydantic import BaseModel
from collections import deque

# Store last N early warning events (Beta only)
EARLY_WARNING_HISTORY = deque(maxlen=200)

router = APIRouter(
    prefix="/api/system",
    tags=["System Signals"],
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

    event = {
        "timestamp": signal.timestamp,
        "status": signal.status,
        "avg_trust": signal.avg_trust,
        "recent_sales": signal.recent_sales,
        "step": signal.step,
        "interventions_triggered": signal.interventions_triggered,
        "context": signal.context,
    }

    # ✅ THIS IS THE MISSING LINE
    EARLY_WARNING_HISTORY.append(event)

    return {
        "ack": True,
        "status": signal.status,
    }
