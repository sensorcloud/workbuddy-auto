from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class OrderCreate(BaseModel):
    user_id: str
    asset_id: str
    selected_quote: Optional[Dict[str, Any]] = None
    container_image: Optional[str] = None
    dataset_location: Optional[str] = None
    task_type: Optional[str] = None
    estimated_duration_hours: Optional[float] = None


class OrderResponse(BaseModel):
    id: str
    user_id: str
    asset_id: str
    status: str
    compute_cost: Optional[float] = None
    energy_cost: Optional[float] = None
    total_cost: Optional[float] = None
    selected_quote: Optional[Dict[str, Any]] = None
    container_image: Optional[str] = None
    dataset_location: Optional[str] = None
    task_type: Optional[str] = None
    estimated_duration_hours: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
