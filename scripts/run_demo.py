# scripts/run_demo.py

import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from authority.authority_decision import authority_decision
from governance.audit_log import create_audit_log


def run_demo():
    print("\n==============================")
    print(" AI GOVERNANCE — TEXT DEMO")
    print("==============================\n")

    decision_event = authority_decision(
        incident_id=42,
        decision="OVERRIDDEN",
        reason="Contextual market volatility not captured by model",
        decided_by="market_fairness_lead"
    )

    print("FINAL HUMAN DECISION\n")
    for k, v in decision_event.items():
        print(f"{k}: {v}")

    audit_entry = create_audit_log(decision_event)

    print("\n------------------------------")
    print("AUDIT LOG (IMMUTABLE RECORD)\n")
    for k, v in audit_entry.items():
        print(f"{k}: {v}")

    print("\n==============================")
    print(" Demo completed successfully ")
    print("==============================\n")


if __name__ == "__main__":
    run_demo()
