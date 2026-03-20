import random

class Merchant:
    def __init__(self, id):
        self.id = id

        # --- economics ---
        self.cost = random.uniform(20, 80)
        self.margin_expectation = random.uniform(1.2, 2.5)
        self.price_multiplier = 1.0

        # --- trust & behavior ---
        self.truthfulness = random.uniform(0.5, 1.0)
        self.trust = 0.5

        # --- claims ---
        self.claim_rate = random.uniform(0.1, 0.6)
        self.claim_rate_multiplier = 1.0

    def issue_claim(self):
        """
        Whether the merchant issues a claim this step.
        Scenario can amplify claim rate via multiplier.
        """
        effective_rate = self.claim_rate * self.claim_rate_multiplier
        return random.random() < min(effective_rate, 1.0)

    def claim_is_true(self):
        """
        Whether the issued claim is actually true.
        """
        return random.random() < self.truthfulness
