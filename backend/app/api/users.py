from fastapi import APIRouter, Depends
from typing import Optional

router = APIRouter()

@router.get("/me")
async def get_current_user():
    # TODO: Implement get current user
    return {"id": 1, "username": "testuser", "email": "test@example.com", "role": "consumer"}
