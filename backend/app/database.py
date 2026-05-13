"""
数据库连接和初始化
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 创建数据库引擎
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    connect_args={"check_same_thread": False} if "sqlite" in settings.SQLALCHEMY_DATABASE_URI else {},
    echo=True
)

# 创建SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """初始化数据库"""
    # 导入所有模型确保 create_all 能创建所有表
    from app.models import User, Asset, Order, Payment, Wallet, Transaction
    from app.models import MonthlyBill, Invoice, MetricSample, AlertRule, Alert, SpotConfig
    from app.models.base import Base
    Base.metadata.create_all(bind=engine)
    print("Database initialized with all Phase 2 tables")

def close_db():
    """关闭数据库连接"""
    engine.dispose()
    print("Database connection closed")

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
