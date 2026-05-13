from fastapi import APIRouter

api_router = APIRouter()

# 导入所有 API 路由模块
from app.api import (
    auth,
    users,
    assets,
    marketplace,
    scheduling,
    orders,
    payments,
    monitoring,
    earnings,
    wallet,   # 新增
    billing,  # 新增
)
