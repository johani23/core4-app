from fastapi import Request

def privatization_headers():
    # Anti-index, anti-preview, anti-embed. This is the “invisibility layer”.
    return {
        "X-Robots-Tag": "noindex, nofollow, noarchive, nosnippet, noimageindex",
        "Cache-Control": "no-store, max-age=0",
        "Pragma": "no-cache",
        "Referrer-Policy": "no-referrer",
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        "Cross-Origin-Opener-Policy": "same-origin",
        "Cross-Origin-Resource-Policy": "same-origin",
    }

def client_key(request: Request, user_id: str | None):
    # For rate limiting keys
    ip = request.client.host if request.client else "unknown"
    return f"user:{user_id}" if user_id else f"ip:{ip}"
