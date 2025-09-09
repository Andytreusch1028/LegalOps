"""
User Management Endpoints
"""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user, require_roles
from app.models.user import User
from app.schemas.auth import UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get current user information"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Update current user information"""
    user_service = UserService(db)
    updated_user = await user_service.update_user(str(current_user.id), user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return updated_user


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: bool = Query(None),
    current_user: User = Depends(require_roles("admin")),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get all users (admin only)"""
    user_service = UserService(db)
    users = await user_service.get_all(skip=skip, limit=limit, is_active=is_active)
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(require_roles("admin")),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get user by ID (admin only)"""
    user_service = UserService(db)
    user = await user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(require_roles("admin")),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Update user by ID (admin only)"""
    user_service = UserService(db)
    updated_user = await user_service.update_user(user_id, user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return updated_user


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_roles("admin")),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Delete user by ID (admin only)"""
    user_service = UserService(db)
    success = await user_service.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"message": "User deleted successfully"}


@router.post("/{user_id}/activate")
async def activate_user(
    user_id: str,
    current_user: User = Depends(require_roles("admin")),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Activate user (admin only)"""
    user_service = UserService(db)
    success = await user_service.activate_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"message": "User activated successfully"}


@router.post("/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    current_user: User = Depends(require_roles("admin")),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Deactivate user (admin only)"""
    user_service = UserService(db)
    success = await user_service.deactivate_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"message": "User deactivated successfully"}


@router.post("/{user_id}/roles/{role}")
async def add_user_role(
    user_id: str,
    role: str,
    current_user: User = Depends(require_roles("admin")),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Add role to user (admin only)"""
    user_service = UserService(db)
    success = await user_service.add_role(user_id, role)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"message": f"Role '{role}' added to user successfully"}


@router.delete("/{user_id}/roles/{role}")
async def remove_user_role(
    user_id: str,
    role: str,
    current_user: User = Depends(require_roles("admin")),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Remove role from user (admin only)"""
    user_service = UserService(db)
    success = await user_service.remove_role(user_id, role)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"message": f"Role '{role}' removed from user successfully"}
