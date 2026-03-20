# ====================================================================
# 💚 Core4.AI – Market Request Router (FINAL CLEAN)
# ====================================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_db
from models.market_request import MarketRequest
from models.campaign import Campaign


router = APIRouter(
    prefix="/api/market",
    tags=["market"]
)


def _slugify(text: str) -> str:
    return text.strip().lower().replace(" ", "-")


# =====================================================
# CREATE REQUEST
# =====================================================

@router.post("/request")
def create_request(payload: dict, db: Session = Depends(get_db)):
    raw_query = (payload.get("query") or "").strip()

    if not raw_query:
        raise HTTPException(status_code=400, detail="query is required")

    normalized_query = raw_query.lower()

    request = MarketRequest(
        query=normalized_query,
        email=payload.get("email")
    )

    db.add(request)
    db.commit()
    db.refresh(request)

    # =====================================================
    # AUTO CREATE CAMPAIGN WHEN THRESHOLD IS REACHED
    # =====================================================

    threshold = 3

    count = db.query(MarketRequest).filter(
        MarketRequest.query == normalized_query
    ).count()

    if count >= threshold:
        existing_linked = db.query(MarketRequest).filter(
            MarketRequest.query == normalized_query,
            MarketRequest.campaign_id.isnot(None)
        ).first()

        if not existing_linked:
            slug = _slugify(normalized_query)

            existing_campaign = db.query(Campaign).filter(
                Campaign.slug == slug
            ).first()

            if not existing_campaign:
                campaign = Campaign(
                    slug=slug,
                    title=raw_query,
                    retail_price=0,
                    current_price=0,
                    target_buyers=50,
                    channel="auto-demand",
                    status="نشطة"
                )

                db.add(campaign)
                db.commit()
                db.refresh(campaign)

                all_requests = db.query(MarketRequest).filter(
                    MarketRequest.query == normalized_query
                ).all()

                for r in all_requests:
                    r.campaign_id = campaign.id

                db.commit()

    return {
        "success": True,
        "request_id": request.id
    }


# =====================================================
# LIST REQUESTS (GROUPED + TRENDING)
# =====================================================

@router.get("/requests")
def list_requests(db: Session = Depends(get_db)):
    requests = db.query(MarketRequest).all()

    grouped = {}

    for r in requests:
        key = r.query.strip().lower()

        if key not in grouped:
            grouped[key] = {
                "query": r.query,
                "count": 0,
                "campaign_id": r.campaign_id
            }

        grouped[key]["count"] += 1

        if r.campaign_id is not None:
            grouped[key]["campaign_id"] = r.campaign_id

    result = sorted(
        grouped.values(),
        key=lambda x: x["count"],
        reverse=True
    )

    return result[:10]


# =====================================================
# MANUAL CREATE CAMPAIGN FROM REQUEST
# =====================================================

@router.post("/create-campaign-from-request/{request_query}")
def create_campaign_from_request(
    request_query: str,
    db: Session = Depends(get_db)
):
    cleaned_query = request_query.strip().lower()

    if not cleaned_query:
        raise HTTPException(status_code=400, detail="request_query is required")

    slug = _slugify(cleaned_query)

    existing_campaign = db.query(Campaign).filter(
        Campaign.slug == slug
    ).first()

    if existing_campaign:
        matching_requests = db.query(MarketRequest).filter(
            MarketRequest.query == cleaned_query
        ).all()

        for r in matching_requests:
            if r.campaign_id is None:
                r.campaign_id = existing_campaign.id

        db.commit()

        return {
            "success": True,
            "campaign_id": existing_campaign.id,
            "waiting_count": len(matching_requests),
            "already_exists": True
        }

    campaign = Campaign(
        slug=slug,
        title=request_query,
        retail_price=0,
        current_price=0,
        target_buyers=50,
        channel="demand",
        status="نشطة"
    )

    db.add(campaign)
    db.commit()
    db.refresh(campaign)

    matching_requests = db.query(MarketRequest).filter(
        MarketRequest.query == cleaned_query
    ).all()

    waiting_count = len(matching_requests)

    for r in matching_requests:
        r.campaign_id = campaign.id

    db.commit()

    return {
        "success": True,
        "campaign_id": campaign.id,
        "waiting_count": waiting_count,
        "already_exists": False
    }