"""
账单 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.core.security import get_current_user
from app.schemas.billing import MonthlyBillResponse, InvoiceCreateRequest, InvoiceResponse, ReconciliationResponse
from app.services.billing_service import BillingService

router = APIRouter()


class BillGenerateRequest(BaseModel):
    year: int
    month: int


@router.get("/monthly", response_model=MonthlyBillResponse)
async def get_monthly_bill(
    year: int = Query(2026),
    month: int = Query(5),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    查询月度账单（不存在时自动生成）
    """
    user_id = current_user.get("user_id", current_user.get("sub", "current_user"))
    bill = BillingService.get_bill(db, user_id, year, month)
    return MonthlyBillResponse.model_validate(bill)


@router.post("/generate", response_model=MonthlyBillResponse)
async def generate_bill(
    req: BillGenerateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    手动生成月度账单
    """
    user_id = current_user.get("user_id", current_user.get("sub", "current_user"))
    bill = BillingService.generate_monthly_bill(db, user_id, req.year, req.month)
    return MonthlyBillResponse.model_validate(bill)


@router.get("/list")
async def list_bills(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
):
    """
    账单列表（按年月倒序）
    """
    user_id = current_user.get("user_id", current_user.get("sub", "current_user"))
    result = BillingService.list_bills(db, user_id, page, page_size)

    items = [MonthlyBillResponse.model_validate(b).model_dump() for b in result["items"]]
    return {
        "items": items,
        "total": result["total"],
        "page": result["page"],
        "page_size": result["page_size"],
    }


@router.post("/{bill_id}/invoice", response_model=InvoiceResponse)
async def create_invoice(
    bill_id: str,
    req: InvoiceCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    申请发票
    """
    user_id = current_user.get("user_id", current_user.get("sub", "current_user"))

    try:
        invoice = BillingService.create_invoice(db, bill_id, user_id, req.model_dump())
        return InvoiceResponse.model_validate(invoice)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/invoices")
async def list_invoices(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    bill_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """
    发票列表
    """
    user_id = current_user.get("user_id", current_user.get("sub", "current_user"))
    result = BillingService.list_invoices(db, user_id, bill_id, status, page, page_size)

    items = [InvoiceResponse.model_validate(i).model_dump() for i in result["items"]]
    return {
        "items": items,
        "total": result["total"],
        "page": result["page"],
        "page_size": result["page_size"],
    }


@router.get("/reconciliation", response_model=ReconciliationResponse)
async def reconciliation(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    start_date: str = Query(..., description="开始日期 ISO 8601"),
    end_date: str = Query(..., description="结束日期 ISO 8601"),
):
    """
    对账管理
    """
    user_id = current_user.get("user_id", current_user.get("sub", "current_user"))
    result = BillingService.reconcile(db, user_id, start_date, end_date)
    return ReconciliationResponse(**result)
