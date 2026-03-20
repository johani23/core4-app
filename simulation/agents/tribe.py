import random

class Tribe:
    def __init__(self, id):
        self.id = id
        self.strictness = random.uniform(0.4, 0.9)
        self.reputation = 0.5

    def validate_claim(self, is_true):
        accuracy = self.strictness
        if is_true:
            return random.random() < accuracy
        else:
            return random.random() > accuracy
