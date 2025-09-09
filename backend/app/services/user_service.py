"""
User Service
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.schemas.auth import UserCreate, UserUpdate
from app.core.security import get_password_hash


class UserService:
    """User service for database operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[User]:
        """Get all users with pagination"""
        query = select(User)
        
        if is_active is not None:
            query = query.where(User.is_active == is_active)
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create new user"""
        hashed_password = get_password_hash(user_data.password)
        
        user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            company_name=user_data.company_name,
            phone=user_data.phone,
            roles=["user"]
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """Update user"""
        update_data = user_data.dict(exclude_unset=True)
        
        if not update_data:
            return await self.get_by_id(user_id)
        
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_by_id(user_id)
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user (soft delete by deactivating)"""
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_active=False)
        )
        await self.db.commit()
        return True
    
    async def activate_user(self, user_id: str) -> bool:
        """Activate user"""
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_active=True)
        )
        await self.db.commit()
        return True
    
    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user"""
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_active=False)
        )
        await self.db.commit()
        return True
    
    async def verify_user(self, user_id: str) -> bool:
        """Verify user email"""
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_verified=True)
        )
        await self.db.commit()
        return True
    
    async def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        from datetime import datetime
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(last_login=datetime.utcnow())
        )
        await self.db.commit()
        return True
    
    async def add_role(self, user_id: str, role: str) -> bool:
        """Add role to user"""
        user = await self.get_by_id(user_id)
        if not user:
            return False
        
        user.add_role(role)
        await self.db.commit()
        return True
    
    async def remove_role(self, user_id: str, role: str) -> bool:
        """Remove role from user"""
        user = await self.get_by_id(user_id)
        if not user:
            return False
        
        user.remove_role(role)
        await self.db.commit()
        return True
    
    async def get_users_by_role(self, role: str) -> List[User]:
        """Get all users with specific role"""
        result = await self.db.execute(
            select(User).where(User.roles.contains([role]))
        )
        return result.scalars().all()
    
    async def search_users(self, query: str) -> List[User]:
        """Search users by name or email"""
        search_term = f"%{query}%"
        result = await self.db.execute(
            select(User).where(
                (User.first_name.ilike(search_term)) |
                (User.last_name.ilike(search_term)) |
                (User.email.ilike(search_term)) |
                (User.company_name.ilike(search_term))
            )
        )
        return result.scalars().all()
