import random
from engine.pricing import mit_price
from engine.claims import process_claim
from engine.trust_renewal import TrustRenewalEngine
from engine.tribe_calibrator import TribeAutoCalibrator
from engine.guardrails import MarketGuardrails
from engine.early_warning import EarlyWarningEngine
from engine.auto_intervention import AutoInterventionEngine
from config import (
    TRUST_DECAY,
    TRUST_BOOST,
    CLAIM_FALSE_PENALTY,
    CLAIM_TRUE_BOOST,
)

class MarketEngine:
    def __init__(
        self,
        buyers,
        merchants,
        tribes,
        tracker,
        enable_trust_renewal=True,
        enable_auto_calibration=True,
        enable_guardrails=True,
    ):
        self.buyers = buyers
        self.merchants = merchants
        self.tribes = tribes
        self.tracker = tracker

        # Feature flags
        self.enable_trust_renewal = enable_trust_renewal
        self.enable_auto_calibration = enable_auto_calibration
        self.enable_guardrails = enable_guardrails

        # Engines
        self.trust_renewal = TrustRenewalEngine()
        self.tribe_calibrator = TribeAutoCalibrator()
        self.guardrails = MarketGuardrails()
        self.early_warning = EarlyWarningEngine()
        self.auto_intervention = AutoInterventionEngine()

        self.step_count = 0
        self.window_size = 100
        self.last_warning_status = "GREEN"

    def step(self):
        self.step_count += 1

        buyer = random.choice(self.buyers)
        merchant = random.choice(self.merchants)
        tribe = random.choice(self.tribes)

        # Pricing
        price = mit_price(
            merchant.cost,
            merchant.trust,
            buyer.memory,
            merchant.price_multiplier,
        )

        # Buyer decision
        decision = buyer.decide(price, merchant.trust)

        # Claim processing
        claim_result = process_claim(merchant, tribe)

        # Purchase outcome
        if decision:
            buyer.update_memory(True)
            merchant.trust += TRUST_BOOST
            self.tracker.record_sale(price, merchant.id)
        else:
            buyer.update_memory(False)
            merchant.trust -= TRUST_DECAY

        # Claim effects
        if claim_result:
            is_true, validated = claim_result

            if validated:
                buyer.memory += 0.02
            else:
                buyer.memory -= 0.03

            if is_true and validated:
                merchant.trust += CLAIM_TRUE_BOOST
                buyer.memory += 0.03
                self.tracker.record_claim(True)
            elif not is_true:
                merchant.trust -= CLAIM_FALSE_PENALTY
                buyer.memory -= 0.05
                self.tracker.record_claim(False)

        # Safety bounds
        merchant.trust = min(max(merchant.trust, 0), 1)
        buyer.memory = min(max(buyer.memory, 0), 1)

        # =========================
        # EARLY WARNING + INTERVENTION
        # =========================
        if self.step_count % self.window_size == 0:
            avg_trust = sum(m.trust for m in self.merchants) / len(self.merchants)
            recent_sales = self.tracker.sales

            status = self.early_warning.evaluate(avg_trust, recent_sales)
            self.last_warning_status = status

            self.auto_intervention.intervene(
                status,
                self.buyers,
                self.merchants,
                self.tribes,
            )

            if self.enable_trust_renewal:
                self.trust_renewal.maybe_renew(
                    self.step_count,
                    self.buyers,
                    self.merchants,
                    self.tribes,
                )

            if self.enable_auto_calibration:
                self.tribe_calibrator.calibrate(
                    self.merchants,
                    self.tribes,
                )

            if self.enable_guardrails:
                self.guardrails.enforce(self.merchants)
