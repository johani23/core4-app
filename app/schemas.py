from pydantic import BaseModel, EmailStr
from datetime import datetime

class LoginReq(BaseModel):
    email: EmailStr
    password: str

class TokenResp(BaseModel):
    token: str
    role: str

class PostCreate(BaseModel):
    category: str
    content: str

class PostOut(BaseModel):
    id: int
    author_id: int
    category: str
    content: str
    created_at: datetime
    likes: int

class ChatSend(BaseModel):
    receiver_id: int
    category: str
    text: str

class CommitmentCreate(BaseModel):
    category: str
    solution_tag: str
    price_point: float
    is_deposit: bool = False

class GravityOut(BaseModel):
    category: str
    gi: float
    rho: float
    vn: float
    cc: float
    mode: str

class GravityConfigUpsert(BaseModel):
    category: str
    gt_threshold: float = 1.0
    w_rho: float = 0.45
    w_vn: float = 0.30
    w_cc: float = 0.25

class SummonsOut(BaseModel):
    id: int
    category: str
    market_size_units: int
    fixed_price_point: float
    conversion_probability: float
    leakage_risk: str
    window_hours: int
    status: str
    created_at: datetime
