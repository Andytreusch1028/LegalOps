"""
Services Endpoints
"""

from typing import Any
from fastapi import APIRouter, Depends

from app.core.security import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.get("/")
async def get_services(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get available services"""
    return {"message": "Services endpoint - coming soon"}


@router.get("/{service_id}")
async def get_service(
    service_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get service by ID"""
    return {"message": f"Service {service_id} - coming soon"}
