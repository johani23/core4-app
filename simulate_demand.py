import requests
import random

URL = "http://127.0.0.1:8000/api/market/commit"
MARKET_ID = "electronics"

def simulate(n=30):
    for i in range(n):
        payload = {
            "market_id": MARKET_ID,
            "buyer_id": f"auto_buyer_{i}",
            "qty": random.randint(1, 3),
            "intent_type": "buy",
            "weight": round(random.uniform(0.7, 1.0), 2),
            "credibility_score": round(random.uniform(0.7, 0.95), 2),
            "current_price": 199
        }

        r = requests.post(URL, json=payload)

        if r.status_code != 200:
            print("Error:", r.text)
        else:
            print(f"Commit {i+1} OK")

    print("✅ Simulation Complete")


if __name__ == "__main__":
    simulate(30)
