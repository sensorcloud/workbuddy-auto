from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.database import get_db
from app.services.scheduling_service import SchedulingService

router = APIRouter()


class QuoteRequest(BaseModel):
    task_type: str
    strategy: str = "cheapest"
    estimated_duration_hours: float = 1.0


class ValidateRequest(BaseModel):
    container_image: str
    dataset_location: Optional[str] = None
    task_type: str = "inference"
    estimated_duration_hours: float = 1.0
    strategy: str = "cheapest"


class TaskSubmitRequest(BaseModel):
    selected_quote: dict
    container_image: Optional[str] = None
    dataset_location: Optional[str] = None
    task_type: Optional[str] = None
    estimated_duration_hours: Optional[float] = None


@router.post("/validate")
async def validate_task(request: ValidateRequest):
    """验证任务参数"""
    if not request.container_image:
        raise HTTPException(status_code=400, detail="容器镜像不能为空")
    if request.estimated_duration_hours <= 0:
        raise HTTPException(status_code=400, detail="预估时长必须大于0")

    return {
        "valid": True,
        "message": "任务参数验证通过",
    }


@router.post("/quote")
async def get_quote(request: QuoteRequest, db: Session = Depends(get_db)):
    """获取智能报价"""
    result = SchedulingService.get_quote(
        db,
        task_type=request.task_type,
        strategy=request.strategy,
        estimated_duration_hours=request.estimated_duration_hours,
    )

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return {
        "quotes": result.get("quotes", []),
        "recommended_quote": result.get("recommended"),
    }


@router.post("/tasks")
async def submit_task(request: TaskSubmitRequest, db: Session = Depends(get_db)):
    """提交任务"""
    # 从 quote 中获取 asset_id
    asset_id = request.selected_quote.get("asset_id", "unknown") if request.selected_quote else "unknown"

    result = SchedulingService.submit_task(
        db,
        user_id="current_user",  # TODO: 从JWT中获取
        asset_id=asset_id,
        task_config={
            "task_type": request.task_type,
            "estimated_hours": request.estimated_duration_hours,
            "container_image": request.container_image,
            "dataset_location": request.dataset_location,
            "selected_quote": request.selected_quote,
        },
    )

    return result
