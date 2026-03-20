def mit_price(cost, trust, demand, price_multiplier=1.0):
    """
    MIT pricing with explicit scenario-driven price multiplier.
    """
    base = cost * (1.3 + demand) * price_multiplier
    trust_modifier = 1 + (trust - 0.5)

    return round(base * trust_modifier, 2)
