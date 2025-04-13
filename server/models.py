from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class UserCreate(UserBase):
    password: Optional[str] = None
    oauth_provider: Optional[str] = None
    oauth_id: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool
    subscription_tier: str = "free"
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User

class TokenData(BaseModel):
    email: Optional[str] = None
    oauth_id: Optional[str] = None

class SubscriptionTier(str, Enum):
    FREE = "free"
    PREMIUM = "premium"
    PRO = "pro"
