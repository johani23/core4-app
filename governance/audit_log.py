def create_audit_log(event):
    return {
        "event_id": event["incident_id"],
        "ai_output": "APPROVE",
        "risk_flag": "HIGH_IMPACT",
        "human_decision": event["final_status"],
        "decision_owner": event["decision_owner"],
        "decision_reason": event["decision_reason"],
        "timestamp": event["timestamp"],
        "immutable": True
    }
