class MarketGuardrails:
    def __init__(
        self,
        max_claim_rate=0.7,
        min_trust=0.25,
    ):
        self.max_claim_rate = max_claim_rate
        self.min_trust = min_trust

    def enforce(self, merchants):
        for m in merchants:
            if m.claim_rate * m.claim_rate_multiplier > self.max_claim_rate:
                m.claim_rate_multiplier *= 0.8

            if m.trust < self.min_trust:
                m.price_multiplier *= 0.9
