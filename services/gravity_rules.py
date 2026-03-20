def decide_pricing_action(event_type: str, gi: float | None, rho: float | None, cc: float | None):
    """
    Returns tuple: (action_type, delta_pct, reason) or (None, None, None)
    MVP rules (audit-friendly):
    - GRAVITY_SPIKE with strong confidence => increase 5%
    - VOLATILITY_HIGH => discount 10% to stabilize conversion
    """
    gi = gi or 0.0
    rho = rho or 0.0
    cc = cc or 0.0

    if event_type == "GRAVITY_SPIKE":
        if gi >= 0.80 and cc >= 0.65 and rho <= 0.35:
            return ("PRICE_UP", 0.05, f"GRAVITY_SPIKE: gi={gi}, cc={cc}, rho={rho} => +5%")
        return (None, None, "GRAVITY_SPIKE but thresholds not met")

    if event_type == "VOLATILITY_HIGH":
        if rho >= 0.60:
            return ("PRICE_DOWN", -0.10, f"VOLATILITY_HIGH: rho={rho} => -10%")
        return (None, None, "VOLATILITY_HIGH but rho not high enough")

    return (None, None, "No rule matched")
