# Explainable EVC engine (no pricing enforcement)

VALUE_WEIGHTS = {
    "home": {
        "اعتمادية التشغيل": 300,
        "كفاءة الطاقة": 200,
        "سهولة الصيانة": 150,
        "خدمة ما بعد البيع": 250,
        "عمر افتراضي أطول": 350,
    },
    "fashion": {
        "جودة أعلى": 200,
        "راحة الاستخدام": 150,
        "تصميم عصري": 250,
        "علامة تجارية": 300,
    },
    "electronics": {
        "أداء ثابت": 250,
        "توافق تقني": 200,
        "دعم فني": 300,
        "تحديثات مستقبلية": 150,
    }
}

def compute_evc(base_price: float, category: str, value_context: list[str]):
    weights = VALUE_WEIGHTS.get(category, {})
    breakdown, added = [], 0
    for item in value_context:
        w = weights.get(item, 0)
        breakdown.append({"factor": item, "value": w})
        added += w

    return {
        "base_price": base_price,
        "added_value": added,
        "evc": base_price + added,
        "breakdown": breakdown,
    }
