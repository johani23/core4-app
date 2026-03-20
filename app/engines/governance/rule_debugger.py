# ============================================================================
# 💚 Core4.AI — Governance Rule Debugger (SAFE)
# Purpose:
# - Explain rule evaluation
# - NEVER crash on bad rules or bad data
# ============================================================================
from pathlib import Path
import yaml


RULES_PATH = Path(__file__).parent / "governance_rules.yaml"

try:
    with open(RULES_PATH, "r", encoding="utf-8") as f:
        RULES = yaml.safe_load(f) or {}
except Exception as e:
    RULES = {"_error": str(e)}


def _safe_eval(actual, operator, threshold):
    try:
        if operator == ">":
            return actual > threshold
        if operator == ">=":
            return actual >= threshold
        if operator == "<":
            return actual < threshold
        if operator == "<=":
            return actual <= threshold
        if operator == "==":
            return actual == threshold
    except Exception:
        return None  # signal comparison error
    return None


def debug_rules(signals: dict) -> dict:
    results = []

    scenarios = RULES.get("scenarios", {})

    for scenario_key, rule in scenarios.items():
        scenario_result = {
            "scenario": scenario_key,
            "scenario_id": rule.get("id"),
            "matched": True,
            "conditions": []
        }

        for cond in rule.get("trigger", {}).get("all", []):
            signal_name = cond.get("signal")
            operator = cond.get("operator")
            threshold = cond.get("value")
            actual = signals.get(signal_name)

            passed = _safe_eval(actual, operator, threshold)

            scenario_result["conditions"].append({
                "signal": signal_name,
                "operator": operator,
                "threshold": threshold,
                "actual": actual,
                "passed": passed
            })

            if passed is not True:
                scenario_result["matched"] = False

        results.append(scenario_result)

    return {
        "signals": signals,
        "rule_evaluation": results
    }
