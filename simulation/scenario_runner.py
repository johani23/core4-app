from agents.buyer import Buyer
from agents.merchant import Merchant
from agents.tribe import Tribe
from engine.market import MarketEngine
from metrics.tracker import MetricsTracker
from data.seed import seed
from config import *

from scenarios.normal import NormalScenario
from scenarios.high_price import HighPriceScenario
from scenarios.claim_abuse import ClaimAbuseScenario
from scenarios.strong_tribes import StrongTribesScenario

SCENARIOS = [
    NormalScenario,
    HighPriceScenario,
    ClaimAbuseScenario,
    StrongTribesScenario,
]

def run_scenario(Scenario):
    seed()

    buyers = [Buyer(i) for i in range(BUYER_COUNT)]
    merchants = [Merchant(i) for i in range(MERCHANT_COUNT)]
    tribes = [Tribe(i) for i in range(TRIBE_COUNT)]

    # Apply scenario parameters
    for b in buyers:
        b.price_normalizer = Scenario.PRICE_NORMALIZER
        b.memory_weight = Scenario.BUYER_PRICE_MEMORY_WEIGHT

    for m in merchants:
        m.claim_rate_multiplier = Scenario.CLAIM_RATE_MULTIPLIER
        m.price_multiplier = Scenario.PRICE_MULTIPLIER

    for t in tribes:
        t.strictness_multiplier = Scenario.TRIBE_STRICTNESS_MULTIPLIER

    tracker = MetricsTracker(suffix=Scenario.NAME)
    market = MarketEngine(buyers, merchants, tribes, tracker)

    for _ in range(SIMULATION_STEPS):
        market.step()

    tracker.export()
    return tracker.summary()

def run_all():
    results = {}

    for Scenario in SCENARIOS:
        print(f"\nRunning scenario: {Scenario.NAME}")
        results[Scenario.NAME] = run_scenario(Scenario)

    print("\n=== SCENARIO SUMMARY ===")
    for name, summary in results.items():
        print(name, "=>", summary)

if __name__ == "__main__":
    run_all()
