"""
用户认证服务
"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt
import hashlib
import os

from app.models.user import User
from app.schemas.user import UserCreate, UserLogin

# JWT配置
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码 - 使用SHA256 + 盐值哈希"""
    try:
        # 格式: salt:hash
        parts = hashed_password.split(":")
        if len(parts) != 2:
            return False
        salt_hex, stored_hash = parts
        salt = bytes.fromhex(salt_hex)
        # 计算输入密码的哈希
        computed_hash = hashlib.pbkdf2_hmac(
            'sha256',
            plain_password.encode('utf-8'),
            salt,
            100000  # 迭代次数
        ).hex()
        return computed_hash == stored_hash
    except Exception as e:
        print(f"Verify password error: {e}")
        return False


def get_password_hash(password: str) -> str:
    """生成密码哈希 - 使用SHA256 + 随机盐值"""
    # 生成随机盐值
    salt = os.urandom(32)
    # 使用PBKDF2哈希
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000  # 迭代次数
    ).hex()
    # 格式: salt:hash
    return f"{salt.hex()}:{password_hash}"


def create_access_token(data: dict) -> str:
    """创建JWT访问令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def register_user(db: Session, user: UserCreate) -> User:
    """注册新用户"""
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == user.username).first():
        raise ValueError("用户名已存在")
    
    # 检查邮箱是否已存在
    if db.query(User).filter(User.email == user.email).first():
        raise ValueError("邮箱已被注册")
    
    # 创建新用户
    db_user = User(
        id=f"user-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        role=user.role,
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """验证用户登录"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
