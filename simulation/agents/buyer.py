import random

class Buyer:
    def __init__(self, id):
        self.id = id
        self.price_sensitivity = random.uniform(0.2, 1.0)
        self.trust_threshold = random.uniform(0.3, 0.8)
        self.memory = 0.5
        self.fatigue = 0.0

        # === Scenario-tunable parameters ===
        self.price_normalizer = 200
        self.memory_weight = 0.3

    def decide(self, price, trust):
        normalized_price = min(price / self.price_normalizer, 1.0)

        effective_score = (
            trust
            - (normalized_price * self.price_sensitivity)
            - self.fatigue
            + (self.memory * self.memory_weight)
        )

        return effective_score > self.trust_threshold

    def update_memory(self, success: bool):
        if success:
            self.memory += 0.05
            self.fatigue = max(0, self.fatigue - 0.02)
        else:
            self.memory -= 0.07
            self.fatigue += 0.03

        self.memory = min(max(self.memory, 0), 1)
