import time
from fastapi import HTTPException, Request
from .config import settings

# in-memory limiter (OK for MVP; replace with Redis in prod)
_BUCKET = {}

def rate_limit(request: Request, key: str, rpm: int | None = None):
    rpm = rpm or settings.RATE_LIMIT_RPM
    now = int(time.time())
    window = now // 60
    k = f"{key}:{window}"
    count = _BUCKET.get(k, 0) + 1
    _BUCKET[k] = count
    if count > rpm:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
