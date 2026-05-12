"""
FastAPI 应用入口
应用工厂模式，注册路由、中间件、异常处理
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from starlette.requests import Request
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
import time
import logging

from app.api import auth, users, assets, marketplace, scheduling, orders, payments, monitoring, earnings
from app.core.config import settings
from app.core.logging import setup_logging
from app.database import init_db, close_db

# 设置日志
setup_logging()

logger = logging.getLogger(__name__)

def create_application() -> FastAPI:
    """
    应用工厂函数
    创建并配置FastAPI应用实例
    """
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description="算电协同产业互联网平台 API",
        version="1.0.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # 注册CORS中间件
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册可信主机中间件
    application.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )

    # 注册路由
    application.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["认证"])
    application.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["用户"])
    application.include_router(assets.router, prefix=f"{settings.API_V1_STR}/assets", tags=["资产"])
    application.include_router(marketplace.router, prefix=f"{settings.API_V1_STR}/marketplace", tags=["市场"])
    application.include_router(scheduling.router, prefix=f"{settings.API_V1_STR}/scheduling", tags=["调度"])
    application.include_router(orders.router, prefix=f"{settings.API_V1_STR}/orders", tags=["订单"])
    application.include_router(payments.router, prefix=f"{settings.API_V1_STR}/payments", tags=["支付"])
    application.include_router(monitoring.router, prefix=f"{settings.API_V1_STR}/monitoring", tags=["监控"])
    application.include_router(earnings.router, prefix=f"{settings.API_V1_STR}/earnings", tags=["收益"])

    # 全局异常处理器
    @application.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """全局异常处理"""
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": 500,
                "message": "服务器内部错误",
                "data": None,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
        )

    # 启动事件
    @application.on_event("startup")
    def startup_event():
        """应用启动时执行"""
        logger.info("Application starting up...")
        # 初始化数据库连接
        init_db()

    # 关闭事件
    @application.on_event("shutdown")
    def shutdown_event():
        """应用关闭时执行"""
        logger.info("Application shutting down...")
        # 关闭数据库连接
        close_db()

    # 健康检查端点
    @application.get("/health")
    async def health_check():
        """健康检查"""
        return {
            "status": "healthy",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

    return application

app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
