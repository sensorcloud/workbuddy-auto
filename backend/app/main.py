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
import json
from decimal import Decimal
from datetime import datetime

from app.api import auth, users, assets, marketplace, scheduling, orders, payments, monitoring, earnings
from app.api import wallet, billing  # 新增路由导入
from app.core.config import settings
from app.core.logging import setup_logging
from app.database import init_db, close_db, SessionLocal

# 设置日志
setup_logging()

logger = logging.getLogger(__name__)


def _init_seed_data():
    """初始化种子数据（仅在表为空时执行）"""
    from app.models.user import User
    from app.models.asset import Asset
    from app.models.order import Order

    db = SessionLocal()
    try:
        # 检查是否已有数据
        if db.query(User).count() > 0:
            logger.info("Seed data already exists, skipping initialization")
            return

        # 创建模拟 Provider 用户
        provider = User(
            id="provider-001",
            username="provider_001",
            email="provider@demo.com",
            hashed_password="dummy_hash",
            role="provider",
        )
        db.add(provider)

        # 创建模拟 Consumer 用户
        consumer = User(
            id="consumer-001",
            username="consumer_001",
            email="consumer@demo.com",
            hashed_password="dummy_hash",
            role="consumer",
        )
        db.add(consumer)
        db.flush()

        # 创建 20 个模拟 Asset
        gpu_models = ["A100", "H100", "V100", "L40S", "A30"]
        regions = ["华北", "华东", "华南", "西部"]

        for i in range(20):
            gpu = gpu_models[i % len(gpu_models)]
            region = regions[i % len(regions)]
            green_ratio = [30, 50, 70, 85, 95][i % 5]
            pricing_type = "fixed" if i % 3 != 0 else "spot"
            gpu_count = [1, 4, 8][i % 3]
            vram = [40, 80, 160][i % 3]

            asset = Asset(
                id=f"asset-{i+1:03d}",
                name=f"{gpu} GPU集群 #{i+1}",
                owner_id=provider.id,
                type="compute",
                status="online",
                spec={
                    "gpu": gpu,
                    "gpu_count": gpu_count,
                    "vram_total": vram,
                    "cpu": "AMD EPYC 7763",
                    "memory": 512,
                    "storage": 2000,
                    "network_bandwidth": "10Gbps"
                },
                pricing={
                    "type": pricing_type,
                    "unit_price": [5.0, 8.0, 12.0, 15.0, 20.0][i % 5],
                    "compute_price_per_hour": [4.0, 6.0, 10.0, 12.0, 16.0][i % 5],
                    "energy_price_per_hour": [1.0, 2.0, 2.0, 3.0, 4.0][i % 5]
                },
                energy_profile={
                    "power_source": ["火电", "水电", "风电", "光伏", "混合"][i % 5],
                    "green_ratio": green_ratio,
                    "pue": round([1.2, 1.3, 1.4, 1.5, 1.6][i % 5], 1),
                    "carbon_intensity": [0.5, 0.2, 0.1, 0.15, 0.3][i % 5]
                },
                location={
                    "region": region,
                    "datacenter": f"{region}DC-{i+1}",
                    "country": "中国"
                },
                availability_sla=round([99.9, 99.95, 99.99, 99.5, 99.9][i % 5], 2),
                rating=round([4.0, 4.2, 4.5, 4.7, 4.8][i % 5], 1),
                total_orders=[10, 25, 50, 80, 120][i % 5],
                pricing_type=pricing_type,
            )
            db.add(asset)

        # 创建 50 个模拟历史订单
        for i in range(50):
            asset_idx = i % 20
            statuses = ["completed", "running", "paid", "cancelled", "pending"]
            order_status = statuses[i % len(statuses)]

            order = Order(
                id=f"order-{i+1:04d}",
                user_id=consumer.id,
                asset_id=f"asset-{asset_idx+1:03d}",
                status=order_status,
                compute_cost=[8.0, 12.0, 20.0, 30.0, 15.0][i % 5],
                energy_cost=[2.0, 3.0, 5.0, 8.0, 4.0][i % 5],
                total_cost=[10.0, 15.0, 25.0, 38.0, 19.0][i % 5],
                instance_type="compute",
                started_at=datetime.utcnow() if order_status in ("running", "completed") else None,
                completed_at=datetime.utcnow() if order_status == "completed" else None,
            )
            db.add(order)

        db.commit()
        logger.info("Seed data initialized: 2 users, 20 assets, 50 orders")
    except Exception as e:
        logger.error(f"Seed data initialization failed: {e}")
        db.rollback()
    finally:
        db.close()


def _collect_metrics():
    """定时采集监控指标"""
    db = SessionLocal()
    try:
        from app.services.monitoring_service import MonitoringService
        count = MonitoringService.generate_mock_metrics(db)
        if count > 0:
            logger.debug(f"Collected {count} metric samples")
    except Exception as e:
        logger.error(f"Metric collection failed: {e}")
    finally:
        db.close()


def _check_alerts():
    """定时检查告警规则"""
    db = SessionLocal()
    try:
        from app.services.monitoring_service import MonitoringService, AlertService
        from app.models.asset import Asset

        assets = db.query(Asset).filter(Asset.status == "online").all()
        for asset in assets:
            latest = MonitoringService.get_latest_metrics(db, asset.id)
            if latest:
                # 提取数值用于告警检查
                metrics = {}
                for metric_name, data in latest.items():
                    if isinstance(data, dict) and "value" in data:
                        metrics[metric_name] = data["value"]
                    elif isinstance(data, (int, float)):
                        metrics[metric_name] = data
                if metrics:
                    AlertService.check_alert_rules(db, asset.id, metrics)
    except Exception as e:
        logger.error(f"Alert check failed: {e}")
    finally:
        db.close()


def _generate_monthly_bills():
    """定时生成月度账单"""
    db = SessionLocal()
    try:
        from app.services.billing_service import BillingService
        from app.models.user import User

        now = datetime.utcnow()
        users = db.query(User).all()
        for user in users:
            try:
                BillingService.generate_monthly_bill(db, user.id, now.year, now.month)
            except Exception as e:
                logger.error(f"Bill generation failed for user {user.id}: {e}")
        logger.debug(f"Monthly bills generated for {len(users)} users")
    except Exception as e:
        logger.error(f"Bill generation failed: {e}")
    finally:
        db.close()


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
    # 新增路由
    application.include_router(wallet.router, prefix=f"{settings.API_V1_STR}/wallet", tags=["钱包"])
    application.include_router(billing.router, prefix=f"{settings.API_V1_STR}/bills", tags=["账单"])

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
        # 初始化种子数据
        _init_seed_data()

        # 启动定时任务调度器
        from apscheduler.schedulers.background import BackgroundScheduler
        scheduler = BackgroundScheduler()

        # 监控指标采集 - 每5秒
        scheduler.add_job(_collect_metrics, 'interval', seconds=5, id='metric_collect')

        # 告警检查 - 每10秒
        scheduler.add_job(_check_alerts, 'interval', seconds=10, id='alert_check')

        # 月度账单生成 - 每月1日0:30
        scheduler.add_job(_generate_monthly_bills, 'cron', day=1, hour=0, minute=30, id='bill_generation')

        scheduler.start()
        application.state.scheduler = scheduler
        logger.info("Scheduled tasks started")

    # 关闭事件
    @application.on_event("shutdown")
    def shutdown_event():
        """应用关闭时执行"""
        logger.info("Application shutting down...")
        # 关闭定时任务
        if hasattr(application.state, 'scheduler'):
            application.state.scheduler.shutdown(wait=False)
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
