from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "consumer"

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
    
    class Config:
        from_attributes = True
