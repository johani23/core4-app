# ============================================================================
# 💚 Core4AI — Governance Auto-Proposal Engine
# ----------------------------------------------------------------------------
# Creates GovernanceDecision proposals based on incoming signals
# ============================================================================

from typing import Dict, Any
from sqlalchemy.orm import Session

from models.governance_decision import GovernanceDecision
from governance.policies import AUTO_PROPOSAL_RULES


def maybe_create_governance_proposal(
    *,
    db: Session,
    signal: Dict[str, Any],
):
    """
    Evaluate signal against rules.
    If matched → create GovernanceDecision (proposal only).
    """

    for rule in AUTO_PROPOSAL_RULES:
        if signal.get("signal_type") != rule["signal_type"]:
            continue

        if signal.get("severity", 0) < rule["min_severity"]:
            continue

        # 🔒 Create proposal (NO execution)
        decision = GovernanceDecision(
            user_id="system",  # system-generated
            scenario=rule["scenario"],
            scenario_id=signal.get("context_id"),
            signals=signal,
            action=rule["action"],
            governor_required=rule.get("governor_required", True),
            pilot_mode=True,
        )

        db.add(decision)
        db.commit()
        db.refresh(decision)

        return decision  # one proposal per signal max

    return None
