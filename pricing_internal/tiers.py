from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Product Tiers"])

class TierInput(BaseModel):
    dv_low: float
    dv_high: float

class TierOutput(BaseModel):
    lite: float
    standard: float
    premium: float


@router.post("/tiers/generate", response_model=TierOutput)
def generate_tiers(data: TierInput):
    lite = data.dv_low * 0.8
    standard = data.dv_low + (data.dv_high * 0.3)
    premium = data.dv_low + data.dv_high

    return TierOutput(lite=lite, standard=standard, premium=premium)
