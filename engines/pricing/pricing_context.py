# ============================================================================
# 🧠 Core4.AI – Pricing Context Layer
# SAFE, NON-BINDING, NON-NUMERIC OUTPUT
# ============================================================================

from pricing.pricing_engine import compute_best_price


def build_pricing_context(product, rnd=None, competitor_price=None):
    """
    Converts internal pricing engine output into
    merchant-safe descriptive context.
    """

    result = compute_best_price(
        product=product,
        rnd=rnd,
        competitor_price=competitor_price,
    )

    # ----------------------------
    # Derive SAFE descriptors
    # ----------------------------

    # Value support (EVC proxy)
    if result["final_price"] >= result["base_price"]:
        value_support = "مدعومة"
    else:
        value_support = "قيد التحقق"

    # Elasticity (based on dispersion)
    spread = abs(result["ai_best_price"] - result["competitor_price"])
    if spread < 20:
        elasticity = "منخفضة"
    elif spread < 60:
        elasticity = "متوسطة"
    else:
        elasticity = "مرتفعة"

    # Pricing zone
    if elasticity == "منخفضة":
        pricing_zone = "آمنة"
    elif elasticity == "متوسطة":
        pricing_zone = "اختبار"
    else:
        pricing_zone = "مخاطرة"

    # Breakeven (never numeric)
    breakeven_status = (
        "متحقق ضمن التوقعات"
        if result["final_price"] >= result["base_price"]
        else "يتطلب متابعة"
    )

    return {
        # 🔒 SAFE OUTPUT ONLY
        "value_support": value_support,
        "elasticity": elasticity,
        "pricing_zone": pricing_zone,
        "breakeven_status": breakeven_status,

        # Governance signal (descriptive only)
        "governed": result["governed_by_tribe"],
        "governance_context": (
            "تسعير محكوم بإطار ثقة"
            if result["governed_by_tribe"]
            else "تسعير مرن ضمن السوق"
        ),
    }
