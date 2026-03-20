import requests
from datetime import datetime

class EarlyWarningAPISignal:
    def __init__(self, endpoint="http://localhost:8000/api/system/early-warning"):
        self.endpoint = endpoint

    def send(
        self,
        status,
        avg_trust,
        recent_sales,
        step,
        interventions_triggered,
        context=None,
    ):
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": status,
            "avg_trust": avg_trust,
            "recent_sales": recent_sales,
            "step": step,
            "interventions_triggered": interventions_triggered,
            "context": context or {},
        }

        try:
            requests.post(self.endpoint, json=payload, timeout=2)
        except Exception:
            # Silent fail (Public Beta safe)
            pass
