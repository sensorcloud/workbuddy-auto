from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.database import get_db
from app.schemas.asset import AssetCreate, AssetResponse
from app.models.asset import Asset

router = APIRouter()


@router.get("/")
async def get_assets(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    gpu_model: Optional[str] = None,
    min_vram: Optional[float] = None,
    max_price: Optional[float] = None,
    power_source: Optional[str] = None,
    region: Optional[str] = None,
    asset_status: Optional[str] = Query(None, alias="status"),
):
    """获取资产列表（分页格式）"""
    query = db.query(Asset)

    if asset_status:
        query = query.filter(Asset.status == asset_status)
    if gpu_model:
        query = query.filter(Asset.spec["gpu"].as_string() == gpu_model)
    if power_source:
        query = query.filter(Asset.energy_profile["power_source"].as_string() == power_source)
    if region:
        query = query.filter(Asset.location["region"].as_string() == region)

    # 计算总数
    total = query.count()

    offset = (page - 1) * page_size
    assets = query.offset(offset).limit(page_size).all()

    return {
        "items": [AssetResponse.model_validate(a).model_dump() for a in assets],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(asset: AssetCreate, db: Session = Depends(get_db)):
    """注册新资产"""
    db_asset = Asset(
        id=f"asset-{asset.spec.get('gpu', 'unknown')}-{hash(str(asset.dict())) % 10000}",
        owner_id=asset.owner_id,
        type=asset.type,
        spec=asset.spec,
        pricing=asset.pricing,
        energy_profile=asset.energy_profile,
        location=asset.location,
        status="online",
    )

    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)

    return db_asset


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(asset_id: str, db: Session = Depends(get_db)):
    """获取资产详情"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资产不存在"
        )
    return asset


@router.put("/{asset_id}", response_model=AssetResponse)
async def update_asset(asset_id: str, asset: AssetCreate, db: Session = Depends(get_db)):
    """更新资产信息"""
    db_asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not db_asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资产不存在"
        )

    for key, value in asset.dict().items():
        setattr(db_asset, key, value)

    db.commit()
    db.refresh(db_asset)

    return db_asset


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(asset_id: str, db: Session = Depends(get_db)):
    """删除资产"""
    db_asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not db_asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资产不存在"
        )

    db.delete(db_asset)
    db.commit()
