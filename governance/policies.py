# ============================================================================
# 💚 Core4AI — Governance Auto-Proposal Policies
# ----------------------------------------------------------------------------
# Defines WHEN a signal should trigger a governance proposal
# ============================================================================

AUTO_PROPOSAL_RULES = [
    {
        "name": "silence_high_severity",
        "signal_type": "SILENCE",
        "min_severity": 2,
        "scenario": "ENGAGEMENT_RISK",
        "action": "Review pricing or messaging due to silence",
        "governor_required": True,
    },
    {
        "name": "conversion_drop",
        "signal_type": "CONVERSION_DROP",
        "min_severity": 1,
        "scenario": "REVENUE_RISK",
        "action": "Investigate conversion funnel anomaly",
        "governor_required": True,
    },
]
