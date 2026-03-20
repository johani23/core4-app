import random
import time
import requests

API_BASE = "http://127.0.0.1:8000"
MARKET_ID = "electronics"

def run(n: int = 25, current_price: float = 199.0, sleep_ms: int = 50):
    url = f"{API_BASE}/api/market/commit"

    ok = 0
    fails = 0

    for i in range(1, n + 1):
        payload = {
            "market_id": MARKET_ID,
            "buyer_id": f"demo_buyer_{i:03d}",
            "qty": random.randint(1, 3),
            "intent_type": "buy",
            "weight": round(random.uniform(0.75, 1.0), 2),
            "credibility_score": round(random.uniform(0.75, 0.95), 2),
            "current_price": current_price,
        }

        try:
            r = requests.post(url, json=payload, timeout=10)
            if r.status_code != 200:
                fails += 1
                print(f"❌ {i}/{n} status={r.status_code} body={r.text[:200]}")
            else:
                ok += 1
                data = r.json()
                p = data.get("proposal", {})
                g = data.get("gravity", {})
                print(
                    f"✅ {i}/{n} buyers={p.get('reason','')}"
                )
                # Optional: quick peek
                print(
                    f"   GI={g.get('gi')} buyers24h={p.get('reason','')} guardrail={p.get('guardrail_status')}"
                )
        except Exception as e:
            fails += 1
            print(f"❌ {i}/{n} exception={e}")

        if sleep_ms > 0:
            time.sleep(sleep_ms / 1000.0)

    print(f"\nDONE ✅ ok={ok} fails={fails}")
    print(f"Now open: {API_BASE}/api/market/state/{MARKET_ID}")

if __name__ == "__main__":
    run(n=25, current_price=199.0, sleep_ms=30)
