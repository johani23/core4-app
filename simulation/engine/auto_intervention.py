class AutoInterventionEngine:
    def __init__(
        self,
        price_soft_cut=0.95,
        price_hard_cut=0.85,
        claim_soft_cut=0.9,
        claim_hard_cut=0.7,
        tribe_soft_step=0.05,
        tribe_hard_step=0.15,
        buyer_memory_soft=0.05,
        buyer_memory_hard=0.12,
    ):
        self.price_soft_cut = price_soft_cut
        self.price_hard_cut = price_hard_cut
        self.claim_soft_cut = claim_soft_cut
        self.claim_hard_cut = claim_hard_cut
        self.tribe_soft_step = tribe_soft_step
        self.tribe_hard_step = tribe_hard_step
        self.buyer_memory_soft = buyer_memory_soft
        self.buyer_memory_hard = buyer_memory_hard

    def intervene(self, status, buyers, merchants, tribes):
        if status == "GREEN":
            return

        # =========================
        # 🟡 SOFT INTERVENTION
        # =========================
        if status == "YELLOW":
            for m in merchants:
                m.price_multiplier *= self.price_soft_cut
                m.claim_rate_multiplier *= self.claim_soft_cut

            for t in tribes:
                t.strictness_multiplier += self.tribe_soft_step

            for b in buyers:
                b.memory += self.buyer_memory_soft

        # =========================
        # 🔴 HARD INTERVENTION
        # =========================
        elif status == "RED":
            for m in merchants:
                m.price_multiplier *= self.price_hard_cut
                m.claim_rate_multiplier *= self.claim_hard_cut

            for t in tribes:
                t.strictness_multiplier += self.tribe_hard_step

            for b in buyers:
                b.memory += self.buyer_memory_hard

        # =========================
        # SAFETY BOUNDS
        # =========================
        for m in merchants:
            m.price_multiplier = max(0.6, min(m.price_multiplier, 1.5))
            m.claim_rate_multiplier = max(0.1, min(m.claim_rate_multiplier, 2.0))

        for t in tribes:
            t.strictness_multiplier = min(t.strictness_multiplier, 2.5)

        for b in buyers:
            b.memory = min(max(b.memory, 0), 1)
