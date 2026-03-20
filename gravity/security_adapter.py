from security.oauth2 import get_current_user
from security.base import UserContext  # or whatever you use

def require_role(user: UserContext, role: str):
    if user.role != role:
        raise PermissionError("Forbidden")
    return user
