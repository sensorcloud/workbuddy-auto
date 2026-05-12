"""
安全工具模块
JWT Token生成与验证、密码哈希与验证
"""
from datetime import datetime, timedelta
from typing import Any, Union
import jwt
from passlib.context import CryptContext
from jose import JWTError, jwt
from app.core.config import settings
from app.schemas.response import ApiResponse

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(subject: Union[str, Any]) -> str:
    """
    创建JWT访问令牌
    
    Args:
        subject: 令牌主题（通常是用户ID）
        
    Returns:
        str: JWT令牌字符串
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: Union[str, Any]) -> str:
    """
    创建JWT刷新令牌
    
    Args:
        subject: 令牌主题（通常是用户ID）
        
    Returns:
        str: JWT刷新令牌字符串
    """
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """
    验证JWT令牌
    
    Args:
        token: JWT令牌字符串
        
    Returns:
        dict: 解码后的令牌数据
        
    Raises:
        JWTError: 令牌验证失败
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        raise JWTError(f"Token验证失败: {str(e)}")

def get_current_user_id(token: str) -> str:
    """
    从令牌中获取当前用户ID
    
    Args:
        token: JWT令牌字符串
        
    Returns:
        str: 用户ID
        
    Raises:
        JWTError: 令牌验证失败
    """
    payload = verify_token(token)
    user_id = payload.get("sub")
    
    if user_id is None:
        raise JWTError("令牌中缺少用户ID")
    
    return user_id

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希后的密码
        
    Returns:
        bool: 密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    生成密码哈希
    
    Args:
        password: 明文密码
        
    Returns:
        str: 哈希后的密码
    """
    return pwd_context.hash(password)

def create_tokens(user_id: str) -> dict:
    """
    为用户创建访问令牌和刷新令牌
    
    Args:
        user_id: 用户ID
        
    Returns:
        dict: 包含access_token和refresh_token的字典
    """
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }
