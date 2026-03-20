# ============================================================================
# 💸 Core4.AI – Pricing Engine
# Feature × Audience × Competitor × Tribe Governance
# FINAL OFFICIAL PRODUCTION VERSION
# ============================================================================

import os
from datetime import datetime, timedelta

from db import SessionLocal

from models.tribe_signal import TribeSignal


# ----------------------------------------------------------------------------
# 🔐 GLOBAL GOVERNANCE SWITCH (KILL SWITCH)
# ----------------------------------------------------------------------------
TRIBE_GOVERNANCE_ENABLED = os.getenv(
    "TRIBE_GOVERNANCE_ENABLED", "true"
).lower() == "true"

STALE_DAYS = 90  # Anti-staleness window


# ----------------------------------------------------------------------------
# 🛡 Tribe Governance Layer (INTERNAL — HARD CONSTRAINTS)
# ----------------------------------------------------------------------------
def _apply_tribe_governance(base_price: float, product_id: str) -> dict:
    """
    Applies hard pricing constraints imposed by Tribe governance.
    This layer is:
    - Optional (can be disabled via ENV)
    - Safe (fails open)
    - Non-overridable by AI or merchants
    """

    # ------------------------------------------------------------
    # Kill switch — instant fallback
    # ------------------------------------------------------------
    if not TRIBE_GOVERNANCE_ENABLED:
        return {
            "min_price": None,
            "discount_allowed": True,
            "governed": False,
            "reason": "governance_disabled",
        }

    db = SessionLocal()
    try:
        signal = (
            db.query(TribeSignal)
            .filter(TribeSignal.product_id == product_id)
            .order_by(TribeSignal.evaluated_at.desc())
            .first()
        )
    except Exception:
        # DB or query failure → fail open
        return {
            "min_price": None,
            "discount_allowed": True,
            "governed": False,
            "reason": "db_failure",
        }
    finally:
        db.close()

    # ------------------------------------------------------------
    # No signal → free market
    # ------------------------------------------------------------
    if not signal:
        return {
            "min_price": None,
            "discount_allowed": True,
            "governed": False,
            "reason": "no_signal",
        }

    # ------------------------------------------------------------
    # Anti-staleness check
    # ------------------------------------------------------------
    try:
        age = datetime.utcnow() - signal.evaluated_at
        if age > timedelta(days=STALE_DAYS):
            return {
                "min_price": None,
                "discount_allowed": True,
                "governed": False,
                "reason": "stale_signal",
            }
    except Exception:
        return {
            "min_price": None,
            "discount_allowed": True,
            "governed": False,
            "reason": "timestamp_error",
        }

    # ------------------------------------------------------------
    # Integrity flag → no governance
    # ------------------------------------------------------------
    if signal.integrity_flag:
        return {
            "min_price": None,
            "discount_allowed": True,
            "governed": False,
            "reason": "integrity_flagged",
        }

    # ------------------------------------------------------------
    # Hard governance condition
    # ------------------------------------------------------------
    if (
        signal.eligibility_state == "trusted"
        and signal.value_per_year == "high"
        and signal.regret_risk < 0.25
    ):
        return {
            # 🔒 HARD PRICE FLOOR (anti race-to-bottom)
            "min_price": round(base_price * 0.95, 2),
            "discount_allowed": False,
            "governed": True,
            "reason": "trusted_tribe",
        }

    # ------------------------------------------------------------
    # Default: free pricing
    # ------------------------------------------------------------
    return {
        "min_price": None,
        "discount_allowed": True,
        "governed": False,
        "reason": "not_eligible",
    }


# ----------------------------------------------------------------------------
# 💰 MAIN PRICING ENGINE (PUBLIC API — BACKWARD COMPATIBLE)
# ----------------------------------------------------------------------------
def compute_best_price(product, rnd=None, competitor_price=None):
    """
    Computes best price using:
    - Feature × Audience logic
    - Competitor anchoring
    - Tribe Governance (hard constraint, optional)
    """

    # ------------------------------------------------------------------------
    # Base inputs
    # ------------------------------------------------------------------------
    base_price = float(product.get("price", 0))
    product_id = product.get("id")

    # Competitor anchoring
    competitor_price = competitor_price or base_price

    # Default audience sensitivity (RND)
    rnd = rnd or {
        "families": 0.8,
        "students": 0.6,
        "women": 0.7,
        "general": 0.5,
    }

    features = product.get("features", [])
    MARKET_COEFFICIENT = 4
    segments = ["families", "students", "women", "general"]

    matrix = []
    segment_totals = {}
    segment_prices = {}

    # ------------------------------------------------------------------------
    # Feature × Segment Matrix
    # ------------------------------------------------------------------------
    for feat in features:
        gap_factor = 1 if feat.get("gap") else 0.4
        seg_obj = {}

        for seg in segments:
            seg_obj[seg] = round(
                feat.get("strength", 1)
                * rnd.get(seg, 0.5)
                * gap_factor
                * MARKET_COEFFICIENT
            )

        matrix.append({
            "name": feat.get("name"),
            "segments": seg_obj,
        })

    # ------------------------------------------------------------------------
    # Totals per segment
    # ------------------------------------------------------------------------
    for seg in segments:
        segment_totals[seg] = sum(f["segments"][seg] for f in matrix)

    # ------------------------------------------------------------------------
    # Segment-based AI pricing
    # ------------------------------------------------------------------------
    for seg in segments:
        segment_prices[seg] = competitor_price + segment_totals[seg]

    best_segment = max(segment_totals, key=segment_totals.get)
    ai_best_price = segment_prices[best_segment]

    # ------------------------------------------------------------------------
    # 🛡 Tribe Governance (FINAL HARD CONSTRAINT)
    # ------------------------------------------------------------------------
    governance = _apply_tribe_governance(
        base_price=base_price,
        product_id=product_id,
    )

    final_price = ai_best_price

    # Enforce price floor if exists
    if governance["min_price"] is not None:
        final_price = max(final_price, governance["min_price"])

    # ------------------------------------------------------------------------
    # FINAL OUTPUT (SAFE + EXTENDED)
    # ------------------------------------------------------------------------
    return {
        # Anchors
        "base_price": base_price,
        "competitor_price": competitor_price,

        # AI internals (unchanged)
        "matrix": matrix,
        "segment_totals": segment_totals,
        "segment_prices": segment_prices,
        "best_segment": best_segment,
        "ai_best_price": round(ai_best_price, 2),

        # Final governed result
        "final_price": round(final_price, 2),
        "discount_allowed": governance["discount_allowed"],
        "governed_by_tribe": governance["governed"],
        "governance_reason": governance["reason"],
    }
