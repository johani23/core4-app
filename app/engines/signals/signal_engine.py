# signal_engine.py
# Core4.AI — Phase 1 Signal Engine (Private Beta)

from datetime import datetime, timedelta
from typing import Dict

# -----------------------------
# Baseline helpers
# -----------------------------

def compute_action_frequency(events, window_minutes=30):
    now = datetime.utcnow()
    window_start = now - timedelta(minutes=window_minutes)
    return len([e for e in events if e["timestamp"] >= window_start])


def compute_time_compression(events):
    if len(events) < 2:
        return 0.0
    times = sorted([e["timestamp"] for e in events])
    deltas = [(times[i+1] - times[i]).seconds for i in range(len(times)-1)]
    return max(0.0, 1 - (sum(deltas) / (len(deltas) * 600)))


def compute_deviation_score(current_vector, baseline_vector):
    # cosine-style simplified deviation
    dot = sum(a*b for a, b in zip(current_vector, baseline_vector))
    norm_a = sum(a*a for a in current_vector) ** 0.5
    norm_b = sum(b*b for b in baseline_vector) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    similarity = dot / (norm_a * norm_b)
    return 1 - similarity


# -----------------------------
# Signal Extraction
# -----------------------------

def extract_signals(user_context: Dict) -> Dict:
    """
    Input: user_context (events, outcomes, history)
    Output: signal dictionary (no decisions)
    """

    events = user_context.get("events", [])
    baseline = user_context.get("baseline", {})
    outcomes = user_context.get("outcomes", [])

    signals = {}

    # Scenario A — Over-Optimization
    signals["action_frequency"] = compute_action_frequency(events)
    signals["time_compression"] = compute_time_compression(events)
    signals["deviation_score"] = compute_deviation_score(
        user_context.get("current_vector", []),
        baseline.get("behavior_vector", [])
    )

    # Scenario B — Emotional Loop
    signals["pattern_recurrence"] = user_context.get("pattern_recurrence", 0)
    signals["avg_outcome_score"] = (
        sum(o["score"] for o in outcomes) / len(outcomes)
        if outcomes else 0
    )
    signals["regret_score"] = user_context.get("regret_score", 0)

    # Scenario C — Silence Collapse
    signals["prior_intensity"] = user_context.get("prior_intensity", 0)
    signals["silence_duration_hours"] = user_context.get("silence_duration_hours", 0)

    return signals
