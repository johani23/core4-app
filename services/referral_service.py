# =========================================================
# 🔗 Referral Service (NO COMMITS)
# =========================================================

from sqlalchemy.orm import Session
from models.growth_event import GrowthEvent


def get_referral_stats(db: Session, campaign_id: int, ref_code: str):
    events = db.query(GrowthEvent).filter(
        GrowthEvent.campaign_id == campaign_id,
        GrowthEvent.ref_code == ref_code,
        GrowthEvent.event_type == "join"
    ).all()

    return {
        "ref_code": ref_code,
        "converted_invites": len(events)
    }