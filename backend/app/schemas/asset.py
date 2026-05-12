from pydantic import BaseModel
from typing import Optional, Dict, Any
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
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
