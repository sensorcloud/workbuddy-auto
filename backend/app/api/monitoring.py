"""
监控API路由
提供任务状态查询接口
"""
from fastapi import APIRouter, Query
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import random

router = APIRouter()

# 模拟的实时数据存储（生产环境应使用Redis或数据库）
_mock_task_data: Dict[str, Dict[str, Any]] = {}


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """
    获取任务状态
    返回前端TaskStatus接口所需的所有字段
    """
    # 从模拟存储中获取任务数据，如果没有则生成模拟数据
    if task_id not in _mock_task_data:
        # 生成模拟的实时数据
        now = datetime.utcnow()
        start_time = now - timedelta(hours=random.uniform(0.5, 3.0))
        progress = min(100, int((now - start_time).total_seconds() / 3600 * 33 + random.uniform(-5, 5)))
        progress = max(0, min(100, progress))
        
        # 生成功耗和碳排放时间序列数据（过去1小时，每10分钟一个点）
        power_kw = [round(random.uniform(2.0, 3.5), 2) for _ in range(6)]
        carbon_kg = [round(p * random.uniform(0.3, 0.5), 2) for p in power_kw]
        timestamps = [
            (now - timedelta(minutes=60 - i * 10)).strftime("%H:%M")
            for i in range(6)
        ]
        
        _mock_task_data[task_id] = {
            "task_id": task_id,
            "order_id": f"order-{task_id[:8]}",
            "asset_id": "asset-001",
            "status": "running" if progress < 100 else "completed",
            "progress": progress,
            "started_at": start_time.isoformat() + "Z",
            "estimated_remaining": f"{max(0, int((100 - progress) / 33))}小时" if progress < 100 else "已完成",
            "running_hours": round((now - start_time).total_seconds() / 3600, 2),
            "total_cost": round(random.uniform(10.0, 50.0), 2),
            "current_power_kw": power_kw[-1],
            "total_compute_cost": round(random.uniform(8.0, 40.0), 2),
            "total_energy_cost": round(random.uniform(2.0, 10.0), 2),
            "total_carbon_kg": round(sum(carbon_kg), 2),
            "real_time_metrics": {
                "power_kw": power_kw,
                "carbon_kg": carbon_kg,
                "timestamps": timestamps,
            },
            "logs": [
                f"[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] 任务启动成功",
                f"[{ (start_time + timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')}] 加载数据集完成",
                f"[{ (start_time + timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S')}] 开始模型推理",
                f"[{ (start_time + timedelta(minutes=20)).strftime('%Y-%m-%d %H:%M:%S')}] 进度 {progress}%",
            ]
        }
    
    return _mock_task_data[task_id]


@router.get("/tasks/{task_id}/logs")
async def get_task_logs(task_id: str, limit: int = Query(50, ge=1, le=1000)):
    """
    获取任务日志
    """
    if task_id not in _mock_task_data:
        return {"logs": []}
    
    logs = _mock_task_data[task_id].get("logs", [])
    return {"logs": logs[-limit:]}


@router.put("/tasks/{task_id}/pause")
async def pause_task(task_id: str):
    """
    暂停任务（待实现）
    """
    return {"status": "success", "message": "暂停任务功能待实现"}


@router.put("/tasks/{task_id}/resume")
async def resumetask(task_id: str):
    """
    恢复任务（待实现）
    """
    return {"status": "success", "message": "恢复任务功能待实现"}
