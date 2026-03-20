# governance_executor.py
# Core4.AI — Phase 1 Governance Executor (Private Beta)

from pathlib import Path
from datetime import datetime
import yaml

# -------------------------------------------------
# Load governance rules
# -------------------------------------------------

RULES_PATH = Path(__file__).parent / "governance_rules.yaml"

with open(RULES_PATH, "r", encoding="utf-8") as f:
    GOVERNANCE_RULES = yaml.safe_load(f)


# -------------------------------------------------
# Helper: evaluate a single condition
# -------------------------------------------------

def _evaluate_condition(signal_value, operator, threshold):
    if operator == ">":
        return signal_value > threshold
    if operator == ">=":
        return signal_value >= threshold
    if operator == "<":
        return signal_value < threshold
    if operator == "<=":
        return signal_value <= threshold
    if operator == "==":
        return signal_value == threshold
    return False


# -------------------------------------------------
# Core evaluator
# -------------------------------------------------

def evaluate(signals: dict, user_id: str) -> dict:
    """
    Input:
      - signals: output from signal_engine
      - user_id: current user
    Output:
      - governance decision (or None)
    """

    for scenario_key, scenario in GOVERNANCE_RULES.get("scenarios", {}).items():

        conditions = scenario["trigger"].get("all", [])
        matched = True
        matched_signals = []

        for cond in conditions:
            signal_name = cond["signal"]
            operator = cond["operator"]
            threshold = cond["value"]

            signal_value = signals.get(signal_name)

            if signal_value is None:
                matched = False
                break

            if not _evaluate_condition(signal_value, operator, threshold):
                matched = False
                break

            matched_signals.append(signal_name)

        if matched:
            return {
                "user_id": user_id,
                "scenario": scenario_key,
                "scenario_id": scenario.get("id"),
                "action": scenario["action"]["type"],
                "governor_required": scenario["action"].get("governor_required", False),
                "copy_key": scenario["action"].get("copy_key"),
                "signals_triggered": matched_signals,
                "timestamp": datetime.utcnow().isoformat()
            }

    return None
