"""
Core4.AI – Visual Impact Ranking Engine (MVP)

- Deterministic, order-sensitive seed
- Objective criteria-based visual ranking (simulated CV-style)
- Light intent-conditioned signal shaping (decision-oriented)
- Arabic explanation with deterministic linguistic variation
- Audit-friendly meta output
"""

# --------------------------------------------------
# Seed logic (order-sensitive, deterministic)
# --------------------------------------------------
def make_seed(post_id: str) -> int:
    return sum(ord(c) * (i + 1) for i, c in enumerate(str(post_id))) % 100


# --------------------------------------------------
# Intent-based signal influence
# (Commercial / decision-oriented)
# --------------------------------------------------
INTENT_BIAS = {
    "attention": {"attraction": +4},
    "convert": {"attraction": +3, "clarity": +2},
    "explain": {"clarity": +5},
    "trust": {"clarity": +3, "balance": +3},
}


# --------------------------------------------------
# Arabic tones (direction)
# --------------------------------------------------
AR_DIRECTION_TONES = {
    "UP": "يؤدي أداءً قويًا مقارنة بالمحتوى المشابه",
    "STEADY": "يحافظ على حضور متوازن ضمن هذا السياق",
    "DOWN": "يواجه منافسة أعلى من المتوسط ضمن هذا السياق",
}


# --------------------------------------------------
# Arabic labels for criteria
# --------------------------------------------------
AR_CRITERIA_LABELS = {
    "attraction": "قوة الجذب",
    "clarity": "الوضوح",
    "originality": "التميّز",
    "attention": "الاحتفاظ بالانتباه",
    "balance": "التوازن البصري",
}


# --------------------------------------------------
# Natural Arabic list formatter
# --------------------------------------------------
def format_signal_list_ar(keys: list[str]) -> str:
    if not keys:
        return "التوازن البصري العام"

    labels = [AR_CRITERIA_LABELS.get(k, k) for k in keys]

    if len(labels) == 1:
        return labels[0]
    if len(labels) == 2:
        return f"{labels[0]} و {labels[1]}"

    return "، ".join(labels[:-1]) + f" و {labels[-1]}"


# --------------------------------------------------
# Linguistic variation templates (deterministic)
# --------------------------------------------------
AR_EXPLANATION_TEMPLATES = [
    "ضمن سياق {context}، {tone}. وبالنظر إلى نية الاستخدام ({intent})، ركّز النظام على {emphasized} عند تقييم قدرة الصورة على دعم القرار.",

    "عند مقارنة هذه الصورة بمحتوى مشابه في سياق {context}، تبيّن أنها {tone}. وقد أثّرت نية الاستخدام ({intent}) على إبراز {emphasized}.",

    "هذه الصورة، ضمن سياق {context}، {tone}. واعتمادًا على نية الاستخدام ({intent})، تم التركيز بشكل أكبر على {emphasized}.",

    "بالمقارنة مع محتوى مماثل ضمن سياق {context}، تحقّق هذه الصورة {tone}. وقد ساهمت نية ({intent}) في تعزيز {emphasized}.",
]


def pick_template(seed: int) -> str:
    return AR_EXPLANATION_TEMPLATES[seed % len(AR_EXPLANATION_TEMPLATES)]


# --------------------------------------------------
# Core analysis
# --------------------------------------------------
def analyze_image(post_id: str, context: str, intent: str) -> dict:
    seed = make_seed(post_id)

    # Relative standing (lower = better)
    percentile = 10 + (seed % 25)  # 10–35%

    # Objective visual criteria (simulated)
    signals = {
        "attraction": 55 + (seed % 20),
        "clarity": 50 + (seed % 25),
        "originality": 52 + (seed % 22),
        "attention": 50 + (seed % 30),
        "balance": 48 + (seed % 30),
    }

    # Apply intent-conditioned shaping
    bias = INTENT_BIAS.get(intent.lower(), {})
    for k, delta in bias.items():
        if k in signals:
            signals[k] = min(100, signals[k] + delta)

    # Direction from percentile
    if percentile <= 18:
        direction = "UP"
    elif percentile <= 28:
        direction = "STEADY"
    else:
        direction = "DOWN"

    emphasized = format_signal_list_ar(list(bias.keys()))
    tone = AR_DIRECTION_TONES[direction]

    template = pick_template(seed)

    explanation = template.format(
        context=context,
        tone=tone,
        intent=intent,
        emphasized=emphasized,
    )

    return {
        "post_id": post_id,
        "context": context,
        "intent": intent,
        "percentile": percentile,
        "direction": direction,
        "signals": signals,
        "explanation": explanation,
        "meta": {
            "seed": seed,
            "intent_bias_applied": list(bias.keys()),
            "criteria_used": list(signals.keys()),
            "engine_version": "visual-impact-beta-v2",
        },
    }
