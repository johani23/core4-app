from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..db import get_db
from ..models import Post, Like, Follow, Commitment
from ..schemas import PostCreate, PostOut, CommitmentCreate
from ..privatization import privatization_headers, client_key
from ..rate_limit import rate_limit
from ..security import decode_token

router = APIRouter(prefix="/social", tags=["social"])

def current_user(request: Request):
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = auth.split(" ", 1)[1]
    payload = decode_token(token)
    return int(payload["sub"]), payload["role"]

@router.post("/posts")
def create_post(payload: PostCreate, request: Request, db: Session = Depends(get_db)):
    uid, _ = current_user(request)
    rate_limit(request, client_key(request, str(uid)), rpm=120)
    p = Post(author_id=uid, category=payload.category, content=payload.content)
    db.add(p); db.commit(); db.refresh(p)
    return {"ok": True, "id": p.id}

@router.get("/feed", response_model=list[PostOut])
def feed(request: Request, category: str | None = None, db: Session = Depends(get_db)):
    uid, _ = current_user(request)
    rate_limit(request, client_key(request, str(uid)), rpm=240)
    q = db.query(Post)
    if category:
        q = q.filter(Post.category == category)
    posts = q.order_by(Post.created_at.desc()).limit(50).all()

    out = []
    for p in posts:
        likes = db.query(func.count(Like.id)).filter(Like.post_id == p.id).scalar() or 0
        out.append(PostOut(id=p.id, author_id=p.author_id, category=p.category, content=p.content, created_at=p.created_at, likes=int(likes)))
    return out

@router.post("/like/{post_id}")
def like(post_id: int, request: Request, db: Session = Depends(get_db)):
    uid, _ = current_user(request)
    rate_limit(request, client_key(request, str(uid)), rpm=240)
    exists = db.query(Like).filter(Like.user_id==uid, Like.post_id==post_id).first()
    if exists:
        db.delete(exists)
        db.commit()
        return {"liked": False}
    l = Like(user_id=uid, post_id=post_id)
    db.add(l); db.commit()
    return {"liked": True}

@router.post("/follow/{user_id}")
def follow(user_id: int, request: Request, db: Session = Depends(get_db)):
    uid, _ = current_user(request)
    if uid == user_id:
        raise HTTPException(400, "Cannot follow yourself")
    exists = db.query(Follow).filter(Follow.follower_id==uid, Follow.followed_id==user_id).first()
    if exists:
        db.delete(exists); db.commit()
        return {"following": False}
    f = Follow(follower_id=uid, followed_id=user_id)
    db.add(f); db.commit()
    return {"following": True}

@router.post("/commit")
def commit(payload: CommitmentCreate, request: Request, db: Session = Depends(get_db)):
    uid, _ = current_user(request)
    c = Commitment(
        user_id=uid,
        category=payload.category,
        solution_tag=payload.solution_tag,
        price_point=payload.price_point,
        is_deposit=payload.is_deposit
    )
    db.add(c); db.commit()
    return {"ok": True}
