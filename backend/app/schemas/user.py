from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "consumer"
    phone: Optional[str] = None  # 手机号
    company_name: Optional[str] = None  # 公司名称

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Optional[Dict] = None

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    phone: Optional[str] = None  # 手机号
    company_name: Optional[str] = None  # 公司名称
    is_active: bool = True
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    phone: Optional[str] = None
    company_name: Optional[str] = None
    email: Optional[str] = None
