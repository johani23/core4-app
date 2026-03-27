# =========================================================
# 👥 Recent Joins Service (NO COMMITS)
# =========================================================

from sqlalchemy.orm import Session
from commitment.models import MarketCommitment


def get_recent_joins(db: Session, campaign_id: int, limit: int = 10):
    joins = (
        db.query(MarketCommitment)
        .filter(MarketCommitment.campaign_id == campaign_id)
        .order_by(MarketCommitment.created_at.desc())
        .limit(limit)
        .all()
    )

    result = []
    for j in joins:
        result.append({
            "email": j.email[:3] + "***",
            "joined_at": j.created_at.isoformat()
        })

    return result