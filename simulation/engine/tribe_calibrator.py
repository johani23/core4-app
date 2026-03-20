class TribeAutoCalibrator:
    def __init__(
        self,
        trust_floor=0.3,
        max_strictness=2.0,
        step_up=0.1,
    ):
        self.trust_floor = trust_floor
        self.max_strictness = max_strictness
        self.step_up = step_up

    def calibrate(self, merchants, tribes):
        avg_trust = sum(m.trust for m in merchants) / len(merchants)

        if avg_trust < self.trust_floor:
            for t in tribes:
                t.strictness_multiplier = min(
                    self.max_strictness,
                    t.strictness_multiplier + self.step_up
                )
            return True

        return False
