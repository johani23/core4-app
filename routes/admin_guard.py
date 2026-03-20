from fastapi import Header, HTTPException, status
import os

ADMIN_KEY = os.getenv("ADMIN_KEY", "dev-admin-secret")

def admin_guard(x_admin_key: str = Header(None)):
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
