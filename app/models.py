from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Boolean, UniqueConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from .db import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_pw: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default="user")  # user|merchant|admin
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    category: Mapped[str] = mapped_column(String(80), index=True)  # e.g. "fitness", "gadgets"
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Like(Base):
    __tablename__ = "likes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint("user_id", "post_id", name="uq_like"),)

class Follow(Base):
    __tablename__ = "follows"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    follower_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    followed_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint("follower_id", "followed_id", name="uq_follow"),)

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    receiver_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    category: Mapped[str] = mapped_column(String(80), index=True)
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class LegacyCommitment(Base):
    """
    Hard commitment signal (MVP): user declares bound preference and optionally deposit/preorder marker.
    In real product: connect to payment/preorder.
    """
    __tablename__ = "commitments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    category: Mapped[str] = mapped_column(String(80), index=True)
    solution_tag: Mapped[str] = mapped_column(String(120))     # e.g. "Protein Bar - 20g - low sugar"
    price_point: Mapped[float] = mapped_column(Float)          # aggregated target
    is_deposit: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class GravityConfig(Base):
    __tablename__ = "gravity_config"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    gt_threshold: Mapped[float] = mapped_column(Float, default=1.0)  # category-specific threshold
    w_rho: Mapped[float] = mapped_column(Float, default=0.45)
    w_vn: Mapped[float] = mapped_column(Float, default=0.30)
    w_cc: Mapped[float] = mapped_column(Float, default=0.25)

class GravityState(Base):
    __tablename__ = "gravity_state"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    gi: Mapped[float] = mapped_column(Float, default=0.0)
    rho: Mapped[float] = mapped_column(Float, default=0.0)
    vn: Mapped[float] = mapped_column(Float, default=0.0)
    cc: Mapped[float] = mapped_column(Float, default=0.0)
    mode: Mapped[str] = mapped_column(String(40), default="INCUBATION")  # INCUBATION|SUMMONS
    last_eval_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Summons(Base):
    __tablename__ = "summons"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String(80), index=True)
    merchant_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    market_size_units: Mapped[int] = mapped_column(Integer)
    fixed_price_point: Mapped[float] = mapped_column(Float)
    conversion_probability: Mapped[float] = mapped_column(Float)
    leakage_risk: Mapped[str] = mapped_column(String(40))  # Low|Med|High
    window_hours: Mapped[int] = mapped_column(Integer, default=72)
    status: Mapped[str] = mapped_column(String(40), default="SENT")  # SENT|ACCEPTED|DECLINED|EXPIRED
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
