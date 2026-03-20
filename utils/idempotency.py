from fastapi import HTTPException

# Simple in-memory store (OK for GA)
# Later → Redis
IDEMPOTENCY_STORE = {}

def check_idempotency(key: str):
    if key in IDEMPOTENCY_STORE:
        raise HTTPException(
            status_code=409,
            detail="Duplicate request detected"
        )
    IDEMPOTENCY_STORE[key] = True
