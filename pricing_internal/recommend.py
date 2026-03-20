from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["AI Recommendation"])

class PricingInputs(BaseModel):
    evc: float
    elasticity: float
    demand_slope: float
    breakeven_units: float
    cost: float

class PricingRecommendation(BaseModel):
    action: str
    optimal_price: float
    reasoning: str


@router.post("/recommend", response_model=PricingRecommendation)
def recommend_price(data: PricingInputs):

    # Positive elasticity = raise price
    if data.elasticity > 0:
        return PricingRecommendation(
            action="increase",
            optimal_price=data.evc,
            reasoning="Positive elasticity luxury signal"
        )

    # Inelastic (>-1)
    if data.elasticity > -1:
        return PricingRecommendation(
            action="increase",
            optimal_price=data.evc * 0.95,
            reasoning="Inelastic -> safe increase"
        )

    # Elastic (-1 to -3)
    if -3 < data.elasticity <= -1:
        return PricingRecommendation(
            action="neutral",
            optimal_price=data.evc * 0.85,
            reasoning="Elastic zone -> breakeven required"
        )

    # Extremely elastic (<-3)
    return PricingRecommendation(
        action="revamp",
        optimal_price=data.cost + 5,
        reasoning="Highly competitive market; product differentiation required"
    )
