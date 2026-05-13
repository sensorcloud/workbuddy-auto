"""通用 Schema 定义"""
from pydantic import BaseModel
from typing import Optional, Generic, TypeVar, List

T = TypeVar("T")

class PaginationParams(BaseModel):
    """分页参数"""
    page: int = 1
    page_size: int = 20

class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应"""
    items: List[T]
    total: int
    page: int
    page_size: int

class SortOption(BaseModel):
    """排序选项"""
    field: str
    order: str = "desc"  # asc / desc
