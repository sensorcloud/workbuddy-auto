"""
资产服务层
"""
from sqlalchemy.orm import Session
from app.models.asset import Asset
from app.schemas.asset import AssetCreate
from datetime import datetime


class AssetService:
    """资产服务类"""
    
    @staticmethod
    def create_asset(db: Session, asset: AssetCreate, owner_id: str) -> Asset:
        """创建资产"""
        import hashlib
        asset_str = str(asset.dict())
        asset_hash = hashlib.md5(asset_str.encode()).hexdigest()[:8]
        gpu_model = asset.spec.get('gpu', 'unknown') if asset.spec else 'unknown'
        
        db_asset = Asset(
            id=f"asset-{gpu_model}-{asset_hash}",
            owner_id=owner_id,
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
    
    @staticmethod
    def list_assets(
        db: Session, 
        asset_type: str = None, 
        status: str = None,
        gpu_model: str = None,
        power_source: str = None,
        region: str = None,
        skip: int = 0,
        limit: int = 100
    ):
        """列出资产"""
        query = db.query(Asset)
        
        if asset_type:
            query = query.filter(Asset.type == asset_type)
        if status:
            query = query.filter(Asset.status == status)
        if gpu_model:
            query = query.filter(Asset.spec["gpu"].as_string() == gpu_model)
        if power_source:
            query = query.filter(Asset.energy_profile["power_source"].as_string() == power_source)
        if region:
            query = query.filter(Asset.location["region"].as_string() == region)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_asset(db: Session, asset_id: str) -> Asset:
        """获取单个资产"""
        return db.query(Asset).filter(Asset.id == asset_id).first()
    
    @staticmethod
    def update_asset(db: Session, asset_id: str, asset_data: dict) -> Asset:
        """更新资产"""
        db_asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not db_asset:
            return None
        
        for key, value in asset_data.items():
            setattr(db_asset, key, value)
        
        db.commit()
        db.refresh(db_asset)
        
        return db_asset
    
    @staticmethod
    def delete_asset(db: Session, asset_id: str) -> bool:
        """删除资产"""
        db_asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not db_asset:
            return False
        
        db.delete(db_asset)
        db.commit()
        
        return True
