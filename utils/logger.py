import logging

logger = logging.getLogger("core4ai")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def log_event(request, action: str, status: str, extra: dict = None):
    payload = {
        "request_id": getattr(request.state, "request_id", None),
        "action": action,
        "status": status,
        "extra": extra or {}
    }
    logger.info(payload)
