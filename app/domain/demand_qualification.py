# app/domain/demand_qualification.py

def qualify_signal(
    tribe_interests: list[str],
    audience_interests: list[str],
    budget_min: int,
    budget_max: int,
    timeframe: str,
    threshold: int,
):
    overlap = set(tribe_interests) & set(audience_interests)

    components = {
        "interest_overlap": len(overlap) * 10,
        "timeframe": 10 if timeframe in ["now", "soon"] else 0,
        "budget_sanity": 5 if budget_max >= budget_min and budget_max > 0 else 0,
    }

    score = sum(components.values())
    qualified = score >= threshold

    reason = (
        f"overlap={len(overlap)}, "
        f"timeframe={timeframe}, "
        f"budget={budget_min}-{budget_max}"
    )

    return {
        "score": score,
        "qualified": qualified,
        "components": components,
        "reason": reason,
    }
