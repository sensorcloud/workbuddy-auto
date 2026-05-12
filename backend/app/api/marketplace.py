from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas.asset import AssetResponse
from app.models.asset import Asset

router = APIRouter()


@router.get("/assets")
async def search_marketplace(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    gpu_model: Optional[str] = None,
    max_price: Optional[float] = None,
    min_vram: Optional[float] = None,
    power_source: Optional[str] = None,
    region: Optional[str] = None,
    asset_status: Optional[str] = Query("online", alias="status"),
):
    """资源市场搜索（只返回在线资源）"""
    query = db.query(Asset).filter(Asset.status == (asset_status or "online"))

    if gpu_model:
        query = query.filter(Asset.spec["gpu"].as_string().ilike(f"%{gpu_model}%"))
    if max_price:
        query = query.filter(Asset.pricing["compute_price_per_hour"].as_float() <= max_price)
    if power_source:
        query = query.filter(Asset.energy_profile["power_source"].as_string() == power_source)
    if region:
        query = query.filter(Asset.location["region"].as_string() == region)

    total = query.count()

    offset = (page - 1) * page_size
    assets = query.offset(offset).limit(page_size).all()

    return {
        "items": [AssetResponse.model_validate(a).model_dump() for a in assets],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
