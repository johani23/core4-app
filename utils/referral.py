# ====================================================================
# 🔗 Core4.AI – Referral Utils (FINAL VERSION)
# ====================================================================

import hashlib
import time
import random


def generate_referral_code(campaign_id: int, email: str) -> str:
    """
    Generates a unique referral code per join event.
    Includes timestamp + randomness for uniqueness.
    """

    raw = f"{campaign_id}:{email.lower()}:{time.time()}:{random.randint(1000,9999)}"

    return hashlib.sha1(
        raw.encode("utf-8")
    ).hexdigest()[:10]


def generate_share_link(campaign_slug: str, ref_code: str) -> str:
    """
    Generates full shareable campaign URL
    """

    return f"/campaign/{campaign_slug}?ref={ref_code}"