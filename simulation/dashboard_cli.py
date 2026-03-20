from agents.buyer import Buyer
from agents.merchant import Merchant
from agents.tribe import Tribe
from engine.market import MarketEngine
from metrics.tracker import MetricsTracker
from data.seed import seed
from config import *

def run_dashboard():
    seed()

    buyers = [Buyer(i) for i in range(BUYER_COUNT)]
    merchants = [Merchant(i) for i in range(MERCHANT_COUNT)]
    tribes = [Tribe(i) for i in range(TRIBE_COUNT)]

    tracker = MetricsTracker(suffix="dashboard")
    market = MarketEngine(buyers, merchants, tribes, tracker)

    for _ in range(SIMULATION_STEPS):
        market.step()

    print("\n=== EARLY WARNING DASHBOARD ===")
    for h in market.dashboard.history:
        print(
            f"Step {h['step']} | "
            f"Trust {h['avg_trust']} | "
            f"Sales {h['recent_sales']} | "
            f"Status {h['status']} | "
            f"Interventions {h['interventions']}"
        )

    print("\nETA to collapse:", market.dashboard.estimate_collapse_eta())

if __name__ == "__main__":
    run_dashboard()
