from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas.order import OrderCreate, OrderResponse
from app.models.order import Order
from datetime import datetime

router = APIRouter()


@router.get("/")
async def get_orders(
    db: Session = Depends(get_db),
    page: int = 1,
    page_size: int = 20,
    order_status: Optional[str] = None,
):
    """获取订单列表（分页格式）"""
    query = db.query(Order)

    if order_status:
        query = query.filter(Order.status == order_status)

    # 计算总数
    total = query.count()

    offset = (page - 1) * page_size
    orders = query.offset(offset).limit(page_size).all()

    return {
        "items": [OrderResponse.model_validate(o).model_dump() for o in orders],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """创建新订单"""
    db_order = Order(
        id=f"order-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        user_id=order.user_id,
        asset_id=order.asset_id,
        status="pending",
        compute_cost=0.0,
        energy_cost=0.0,
        total_cost=0.0,
        selected_quote=order.selected_quote,
        container_image=order.container_image,
        dataset_location=order.dataset_location,
        task_type=order.task_type,
        estimated_duration_hours=order.estimated_duration_hours,
    )

    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    return db_order


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, db: Session = Depends(get_db)):
    """获取订单详情"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    return order


@router.put("/{order_id}/pay", response_model=OrderResponse)
async def pay_order(order_id: str, db: Session = Depends(get_db)):
    """支付订单"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    if order.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="订单状态不允许支付"
        )

    # 更新订单状态
    order.status = "running"
    order.started_at = datetime.utcnow()
    order.compute_cost = order.selected_quote.get("compute_cost", 0) if order.selected_quote else 0
    order.energy_cost = order.selected_quote.get("energy_cost", 0) if order.selected_quote else 0
    order.total_cost = order.compute_cost + order.energy_cost

    db.commit()
    db.refresh(order)

    return order


@router.put("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(order_id: str, db: Session = Depends(get_db)):
    """取消订单"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    if order.status not in ["pending", "running"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="订单状态不允许取消"
        )

    order.status = "cancelled"
    db.commit()
    db.refresh(order)

    return order
