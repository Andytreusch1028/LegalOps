"""
Business Entities Endpoints
"""

from typing import Any
from fastapi import APIRouter, Depends

from app.core.security import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.get("/")
async def get_entities(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get user's business entities"""
    return {"message": "Entities endpoint - coming soon"}


@router.post("/")
async def create_entity(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Create new business entity"""
    return {"message": "Create entity - coming soon"}
