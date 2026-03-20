from datetime import datetime

def authority_decision(
    incident_id: int,
    decision: str,
    reason: str,
    decided_by: str
):
    return {
        "incident_id": incident_id,
        "final_status": decision,
        "decision_reason": reason,
        "decision_owner": decided_by,
        "timestamp": datetime.utcnow().isoformat(),
        "governance": "HUMAN_IN_THE_LOOP"
    }
