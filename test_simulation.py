from services.pricing_simulator import simulate_campaign_growth
from db import SessionLocal

def run():
    db = SessionLocal()

    results = simulate_campaign_growth(db, campaign_id=7)

    for r in results[:20]:
        print(r)

if __name__ == "__main__":
    run()