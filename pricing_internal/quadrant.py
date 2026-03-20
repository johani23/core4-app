from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Pricing Quadrant"])

class QuadrantInput(BaseModel):
    num_price_tests: int
    uses_elasticity: bool
    uses_conjoint: bool
    uses_ab: bool

class QuadrantResult(BaseModel):
    quadrant: str


@router.post("/quadrant")
def pricing_quadrant(data: QuadrantInput):
    score = 0
    score += data.num_price_tests
    score += 2 if data.uses_elasticity else 0
    score += 2 if data.uses_conjoint else 0
    score += 2 if data.uses_ab else 0

    if score >= 6: return {"quadrant":"Superlative"}
    if score >= 3: return {"quadrant":"Adaptive"}
    if score >= 1: return {"quadrant":"Reactive"}
    return {"quadrant":"Primitive"}
