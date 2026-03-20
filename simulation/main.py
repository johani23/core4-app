from agents.buyer import Buyer
from agents.merchant import Merchant
from agents.tribe import Tribe
from engine.market import MarketEngine
from metrics.tracker import MetricsTracker
from data.seed import seed
from config import *

def run():
    seed()

    buyers = [Buyer(i) for i in range(BUYER_COUNT)]
    merchants = [Merchant(i) for i in range(MERCHANT_COUNT)]
    tribes = [Tribe(i) for i in range(TRIBE_COUNT)]

    tracker = MetricsTracker()
    market = MarketEngine(buyers, merchants, tribes, tracker)

    for _ in range(SIMULATION_STEPS):
        market.step()

    tracker.export()
    print("Simulation complete.")
    print("Sales:", tracker.sales)
    print("Revenue:", tracker.revenue)
    print("True Claims:", tracker.true_claims)
    print("False Claims:", tracker.false_claims)

if __name__ == "__main__":
    run()
