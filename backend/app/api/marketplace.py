"""
市场 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel

from app.database import get_db
from app.core.security import get_current_user
from app.schemas.asset import AssetResponse
from app.services.marketplace_service import MarketplaceService

router = APIRouter()


class ReviewCreate(BaseModel):
    order_id: str
    score: int
    text: Optional[str] = None
    anonymous: bool = False


@router.get("/assets")
async def search_assets(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    gpu_model: Optional[str] = Query(None, description="GPU型号筛选"),
    gpu_count: Optional[int] = Query(None, description="GPU数量筛选"),
    vram_min: Optional[int] = Query(None, description="最小显存 GB"),
    region: Optional[str] = Query(None, description="地域筛选"),
    min_price: Optional[Decimal] = Query(None, description="最低价格/小时"),
    max_price: Optional[Decimal] = Query(None, description="最高价格/小时"),
    green_ratio_min: Optional[int] = Query(None, description="最低绿电比例"),
    pue_max: Optional[float] = Query(None, description="最大PUE"),
    sort: Optional[str] = Query("created_desc", description="排序: price_asc|price_desc|rating_desc|created_desc"),
    pricing_type: Optional[str] = Query(None, description="定价类型: fixed|spot"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """
    搜索市场资源
    """
    filters = {}
    if gpu_model:
        filters["gpu_model"] = gpu_model
    if gpu_count:
        filters["gpu_count"] = gpu_count
    if vram_min:
        filters["vram_min"] = vram_min
    if region:
        filters["region"] = region
    if min_price is not None:
        filters["min_price"] = float(min_price)
    if max_price is not None:
        filters["max_price"] = float(max_price)
    if green_ratio_min is not None:
        filters["green_ratio_min"] = green_ratio_min
    if pue_max is not None:
        filters["pue_max"] = pue_max
    if pricing_type:
        filters["pricing_type"] = pricing_type

    result = MarketplaceService.search_assets(db, filters, page, page_size, sort)

    items = []
    for asset in result["items"]:
        items.append(AssetResponse(
            id=asset.id,
            owner_id=asset.owner_id,
            type=asset.type,
            status=asset.status,
            spec=asset.spec if isinstance(asset.spec, dict) else {},
            pricing=asset.pricing if isinstance(asset.pricing, dict) else {},
            energy_profile=asset.energy_profile if isinstance(asset.energy_profile, dict) else {},
            location=asset.location if isinstance(asset.location, dict) else {},
            availability_sla=asset.availability_sla or 99.9,
            rating=asset.rating,
            total_orders=asset.total_orders or 0,
            pricing_type=asset.pricing_type or "fixed",
        ).model_dump())

    return {
        "items": items,
        "total": result["total"],
        "page": result["page"],
        "page_size": result["page_size"],
        "filters_applied": result.get("filters_applied", {}),
    }


@router.get("/assets/{asset_id}")
async def get_asset_detail(
    asset_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    获取资源详情
    """
    result = MarketplaceService.get_asset_detail(db, asset_id)
    if not result:
        raise HTTPException(status_code=404, detail="资源不存在")
    return result


@router.get("/assets/{asset_id}/reviews")
async def get_asset_reviews(
    asset_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """
    获取资源评价列表
    """
    result = MarketplaceService.get_reviews(db, asset_id, page, page_size)
    return result


@router.post("/assets/{asset_id}/reviews")
async def create_review(
    asset_id: str,
    req: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    创建资源评价
    """
    user_id = current_user.get("user_id", current_user.get("sub", "current_user"))
    try:
        result = MarketplaceService.create_review(
            db, asset_id, req.order_id, user_id, req.score, req.text
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
