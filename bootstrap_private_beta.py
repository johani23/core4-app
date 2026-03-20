# ============================================================================
# Core4.AI — Private Beta Bootstrap Script
# SAFE MODE:
# - Creates new folders/files only
# - Does NOT modify existing files
# - Overwrite = False
# ============================================================================

from pathlib import Path

BASE = Path("app")

FILES = {
    # -------------------- Signals Engine --------------------
    BASE / "engines" / "signals" / "__init__.py": "",
    BASE / "engines" / "signals" / "signal_engine.py": '''
from datetime import datetime, timedelta

def extract_signals(user_context: dict) -> dict:
    events = user_context.get("events", [])
    outcomes = user_context.get("outcomes", [])

    signals = {}

    # Over-optimization
    signals["action_frequency"] = len(events)
    signals["time_compression"] = min(len(events) / 10, 1.0)

    baseline_vector = user_context.get("baseline", {}).get("behavior_vector", [])
    current_vector = user_context.get("current_vector", [])

    if baseline_vector and current_vector:
        similarity = sum(a*b for a, b in zip(baseline_vector, current_vector))
        signals["deviation_score"] = 1 - similarity
    else:
        signals["deviation_score"] = 0.0

    # Emotional loop
    signals["pattern_recurrence"] = user_context.get("pattern_recurrence", 0)
    signals["avg_outcome_score"] = (
        sum(o.get("score", 0) for o in outcomes) / len(outcomes)
        if outcomes else 0
    )
    signals["regret_score"] = user_context.get("regret_score", 0)

    # Silence
    signals["prior_intensity"] = user_context.get("prior_intensity", 0)
    signals["silence_duration_hours"] = user_context.get("silence_duration_hours", 0)

    return signals
''',

    # -------------------- Governance Engine --------------------
    BASE / "engines" / "governance" / "__init__.py": "",
    BASE / "engines" / "governance" / "governance_executor.py": '''
from pathlib import Path
from datetime import datetime
import yaml

RULES_PATH = Path(__file__).parent / "governance_rules.yaml"

with open(RULES_PATH, "r", encoding="utf-8") as f:
    RULES = yaml.safe_load(f)

def _eval(val, op, ref):
    return {
        ">": val > ref,
        ">=": val >= ref,
        "<": val < ref,
        "<=": val <= ref,
        "==": val == ref,
    }.get(op, False)

def evaluate(signals: dict, user_id: str):
    for key, rule in RULES.get("scenarios", {}).items():
        if all(
            _eval(signals.get(c["signal"], 0), c["operator"], c["value"])
            for c in rule["trigger"]["all"]
        ):
            return {
                "user_id": user_id,
                "scenario": key,
                "scenario_id": rule.get("id"),
                "action": rule["action"]["type"],
                "governor_required": rule["action"].get("governor_required", False),
                "copy_key": rule["action"].get("copy_key"),
                "signals_triggered": [c["signal"] for c in rule["trigger"]["all"]],
                "timestamp": datetime.utcnow().isoformat()
            }
    return None
''',

    BASE / "engines" / "governance" / "governance_rules.yaml": '''
scenarios:
  over_optimization_risk:
    id: A
    trigger:
      all:
        - { signal: action_frequency, operator: ">", value: 5 }
        - { signal: time_compression, operator: ">", value: 0.6 }
        - { signal: deviation_score, operator: ">", value: 0.7 }
    action:
      type: pause
      governor_required: false
      copy_key: pause_non_accusatory

  emotional_decision_loop:
    id: B
    trigger:
      all:
        - { signal: pattern_recurrence, operator: ">=", value: 3 }
        - { signal: avg_outcome_score, operator: "<", value: -0.4 }
        - { signal: regret_score, operator: ">", value: 0.6 }
    action:
      type: soft_refusal
      governor_required: true
      copy_key: refusal_explanatory
''',

    # -------------------- Decision Log Model --------------------
    BASE / "models" / "governance_decision.py": '''
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from datetime import datetime
from db import Base

class GovernanceDecision(Base):
    __tablename__ = "governance_decisions"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, index=True, nullable=False)
    scenario = Column(String, index=True)
    scenario_id = Column(String, index=True)
    signals = Column(JSON, nullable=False)
    triggered_signals = Column(JSON)
    action = Column(String)
    governor_required = Column(Boolean, default=False)
    copy_key = Column(String)
    pilot_mode = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
'''
}

def safe_write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        print(f"SKIP (exists): {path}")
        return
    path.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"CREATED: {path}")

if __name__ == "__main__":
    for p, c in FILES.items():
        safe_write(p, c)

    print("\\n✅ Private Beta bootstrap completed safely.")
