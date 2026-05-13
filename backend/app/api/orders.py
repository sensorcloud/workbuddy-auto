"""
订单 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel

from app.database import get_db
from app.core.security import get_current_user
from app.schemas.order import OrderCreate, OrderResponse
from app.models.order import Order
from app.services.order_service import OrderService
from app.services.payment_service import PaymentService
from app.services.wallet_service import WalletService
from datetime import datetime

router = APIRouter()


class ReviewCreate(BaseModel):
    score: int
    text: Optional[str] = None


class RefundRequest(BaseModel):
    reason: str
    amount: Optional[Decimal] = None


class StatusHistory(BaseModel):
    status: str
    timestamp: str
    remark: str


@router.get("/")
async def get_orders(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    order_status: Optional[str] = Query(None),
):
    """
    获取订单列表（分页格式）
    """
    user_id = current_user.get("user_id", current_user.get("sub", "current_user"))
    orders = OrderService.list_orders(db, user_id=user_id, status=order_status, skip=(page-1)*page_size, limit=page_size)

    return {
        "items": [OrderResponse.model_validate(o).model_dump() for o in orders],
        "total": len(orders),
        "page": page,
        "page_size": page_size,
    }


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    创建新订单
    """
    user_id = current_user.get("user_id", current_user.get("sub", "current_user"))
    order.user_id = user_id
    db_order = OrderService.create_order(db, order)
    return db_order


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, db: Session = Depends(get_db)):
    """
    获取订单详情
    """
    order = OrderService.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")
    return order


@router.put("/{order_id}/pay", response_model=OrderResponse)
async def pay_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    支付订单（调用 PaymentService）
    """
    user_id = current_user.get("user_id", current_user.get("sub", "current_user"))
    result = PaymentService.create_payment(db, user_id, order_id, "balance")

    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("message", "支付失败"))

    # 重新查询订单
    order = OrderService.get_order(db, order_id)
    return order


@router.put("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    取消订单（包含退款逻辑）
    """
    order = OrderService.cancel_order(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")
    return order


@router.put("/{order_id}/complete", response_model=OrderResponse)
async def complete_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    标记订单完成
    """
    order = OrderService.complete_order(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")
    return order


@router.post("/{order_id}/review")
async def review_order(
    order_id: str,
    req: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    订单评价
    """
    user_id = current_user.get("user_id", current_user.get("sub", "current_user"))
    result = OrderService.review_order(db, order_id, user_id, req.score, req.text)

    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("message", "评价失败"))

    return result


@router.post("/{order_id}/refund")
async def refund_order(
    order_id: str,
    req: RefundRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    申请退款
    """
    user_id = current_user.get("user_id", current_user.get("sub", "current_user"))
    amount = float(req.amount) if req.amount else None
    result = OrderService.refund_order(db, order_id, user_id, req.reason, amount)

    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("message", "退款失败"))

    return result


@router.get("/{order_id}/status-history")
async def get_status_history(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    订单状态变更历史
    """
    history = OrderService.get_status_history(db, order_id)
    if not history:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")
    return history
