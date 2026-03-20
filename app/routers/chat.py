from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import ChatMessage
from ..schemas import ChatSend
from ..security import decode_token
from ..privatization import client_key
from ..rate_limit import rate_limit

router = APIRouter(prefix="/chat", tags=["chat"])

def current_user(request: Request):
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = auth.split(" ", 1)[1]
    payload = decode_token(token)
    return int(payload["sub"]), payload["role"]

@router.post("/send")
def send(payload: ChatSend, request: Request, db: Session = Depends(get_db)):
    uid, _ = current_user(request)
    rate_limit(request, client_key(request, str(uid)), rpm=300)
    msg = ChatMessage(sender_id=uid, receiver_id=payload.receiver_id, category=payload.category, text=payload.text)
    db.add(msg); db.commit()
    return {"ok": True}

@router.get("/inbox")
def inbox(request: Request, db: Session = Depends(get_db)):
    uid, _ = current_user(request)
    rate_limit(request, client_key(request, str(uid)), rpm=240)
    msgs = db.query(ChatMessage).filter((ChatMessage.sender_id==uid) | (ChatMessage.receiver_id==uid))\
        .order_by(ChatMessage.created_at.desc()).limit(80).all()
    return [{
        "id": m.id,
        "sender_id": m.sender_id,
        "receiver_id": m.receiver_id,
        "category": m.category,
        "text": m.text,
        "created_at": m.created_at.isoformat()
    } for m in msgs]
