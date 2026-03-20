class TrustRenewalEngine:
    def __init__(
        self,
        trust_floor=0.35,
        boost_amount=0.08,
        buyer_boost=0.05,
        cooldown=200,
    ):
        self.trust_floor = trust_floor
        self.boost_amount = boost_amount
        self.buyer_boost = buyer_boost
        self.cooldown = cooldown
        self.last_trigger_step = -cooldown

    def maybe_renew(self, step, buyers, merchants, tribes):
        if step - self.last_trigger_step < self.cooldown:
            return False

        avg_trust = sum(m.trust for m in merchants) / len(merchants)

        if avg_trust < self.trust_floor:
            # 🔁 Renew trust
            for m in merchants:
                m.trust += self.boost_amount

            for b in buyers:
                b.memory += self.buyer_boost

            self.last_trigger_step = step
            return True

        return False
