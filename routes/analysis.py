from fastapi import APIRouter
from pydantic import BaseModel
from analysis.engine import analyze_image

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


class AnalysisRequest(BaseModel):
    post_id: str
    context: str
    intent: str


@router.post("/image")
def analyze_image_endpoint(req: AnalysisRequest):
    return analyze_image(
        post_id=req.post_id,
        context=req.context,
        intent=req.intent,
    )
