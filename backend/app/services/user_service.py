"""
用户服务层
"""
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from datetime import datetime


class UserService:
    """用户服务类"""
    
    @staticmethod
    def get_user(db: Session, user_id: str) -> User:
        """获取用户"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User:
        """根据用户名获取用户"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def update_user(db: Session, user_id: str, user_data: dict) -> User:
        """更新用户"""
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None
        
        for key, value in user_data.items():
            setattr(db_user, key, value)
        
        db.commit()
        db.refresh(db_user)
        
        return db_user
