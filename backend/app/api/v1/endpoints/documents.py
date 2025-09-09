"""
Documents Endpoints
"""

from typing import Any
from fastapi import APIRouter, Depends

from app.core.security import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.get("/")
async def get_documents(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get user's documents"""
    return {"message": "Documents endpoint - coming soon"}


@router.post("/upload")
async def upload_document(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Upload document"""
    return {"message": "Upload document - coming soon"}
