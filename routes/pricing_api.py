# ============================================================================
# 💸 Pricing API — Tribe-Governed Pricing
# ============================================================================

from fastapi import APIRouter
from engines.pricing.pricing_engine import compute_best_price

print("🔥 PRICING ROUTER LOADED 🔥")

router = APIRouter(prefix="/api/pricing", tags=["pricing"])


@router.post("/compute")
def compute_price(payload: dict):
    """
    Compute final price using:
    - Feature × Audience logic
    - Tribe governance (if available)
    """
    product = payload.get("product")
    rnd = payload.get("rnd")

    if not product:
        return {"error": "product is required"}

    pricing = compute_best_price(product, rnd)

    return {
        "status": "success",
        "pricing": pricing
    }
