"""
Compliance Endpoints
"""

from typing import Any
from fastapi import APIRouter, Depends

from app.core.security import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.get("/")
async def get_compliance_status(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get compliance status"""
    return {"message": "Compliance endpoint - coming soon"}


@router.get("/calendar")
async def get_compliance_calendar(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get compliance calendar"""
    return {"message": "Compliance calendar - coming soon"}
