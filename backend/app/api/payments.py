"""
支付 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.core.security import get_current_user
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentCallback, PaymentCallbackResult
from app.services.payment_service import PaymentService

router = APIRouter()


@router.post("/create")
async def create_payment(
    req: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    创建支付请求
    - channel="balance": 余额支付，直接成功
    - channel=第三方: 返回支付链接/二维码
    """
    user_id = current_user.get("user_id", current_user.get("sub", "current_user"))
    result = PaymentService.create_payment(db, user_id, req.order_id, req.channel)

    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("message", "支付创建失败"))

    return result


@router.post("/callback/{payment_id}", response_model=PaymentCallbackResult)
async def payment_callback(
    payment_id: str,
    callback: PaymentCallback,
    db: Session = Depends(get_db),
):
    """
    支付回调（供第三方支付网关调用）
    """
    callback_data = callback.model_dump()
    result = PaymentService.handle_callback(db, payment_id, callback_data)

    return PaymentCallbackResult(
        success=result.get("success", False),
        message=result.get("message", "处理失败"),
    )


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    查询支付记录
    """
    payment = PaymentService.get_payment(db, payment_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="支付记录不存在")

    return PaymentResponse.model_validate(payment)


@router.get("/order/{order_id}", response_model=PaymentResponse)
async def get_payment_by_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    根据订单ID查询支付记录
    """
    payment = PaymentService.get_by_order_id(db, order_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="支付记录不存在")

    return PaymentResponse.model_validate(payment)


@router.get("/mock/pay/{payment_id}")
async def mock_pay(
    payment_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    开发用：模拟支付成功（仅供开发测试使用）
    """
    result = PaymentService.mock_pay(db, payment_id)
    return result
