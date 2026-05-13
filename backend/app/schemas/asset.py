from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class AssetCreate(BaseModel):
    owner_id: str
    type: str  # compute, storage
    spec: Dict[str, Any] = {}
    pricing: Dict[str, Any] = {}
    energy_profile: Dict[str, Any] = {}
    location: Dict[str, Any] = {}


class AssetResponse(BaseModel):
    id: str
    owner_id: str
    type: str
    status: str
    spec: Optional[Dict[str, Any]] = None
    pricing: Optional[Dict[str, Any]] = None
    energy_profile: Optional[Dict[str, Any]] = None
    location: Optional[Dict[str, Any]] = None
    availability_sla: Optional[float] = 99.9
    rating: Optional[float] = 0
    total_orders: Optional[int] = 0
    pricing_type: Optional[str] = "fixed"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AssetUpdate(BaseModel):
    spec: Optional[Dict[str, Any]] = None
    pricing: Optional[Dict[str, Any]] = None
    energy_profile: Optional[Dict[str, Any]] = None
    location: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    pricing_type: Optional[str] = None


class AssetSearchParams(BaseModel):
    """资产搜索参数"""
    type: Optional[str] = None  # compute, storage
    status: Optional[str] = None
    owner_id: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    location_region: Optional[str] = None
    min_sla: Optional[float] = None
    min_rating: Optional[float] = None
    keyword: Optional[str] = None


class AssetQuoteRequest(BaseModel):
    """资产报价请求"""
    asset_id: str
    duration_hours: float
    instance_type: str = "on_demand"  # on_demand / reserved / spot
    spot_config: Optional[Dict[str, Any]] = None


class AssetQuoteResponse(BaseModel):
    """资产报价响应"""
    asset_id: str
    base_price: float
    compute_price: float
    energy_price: float
    total_price: float
    period: str  # peak / flat / valley
    multiplier: float
    valid_until: datetime
