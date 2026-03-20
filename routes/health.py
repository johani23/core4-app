# ============================================================================
# 💚 Core4AI – Health & Readiness API
# GA STANDARD HEALTH CHECK
# ============================================================================

from fastapi import APIRouter

router = APIRouter(
    tags=["system"]
)

@router.get("/")
def root_health():
    return {
        "status": "Core4 Backend Running",
        "service": "core4ai",
        "stage": "beta-hardened"
    }

@router.get("/health")
def health():
    return {
        "status": "ok",
        "ga_ready": True
    }

@router.get("/api/health")
def api_health():
    return health()
