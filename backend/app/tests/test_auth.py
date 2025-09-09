"""
Authentication Tests
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


@pytest.mark.asyncio
class TestAuthentication:
    """Test authentication endpoints"""
    
    async def test_register_user(self, client: AsyncClient, db_session: AsyncSession):
        """Test user registration"""
        user_data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
            "first_name": "New",
            "last_name": "User",
            "company_name": "New Company"
        }
        
        response = await client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["first_name"] == user_data["first_name"]
        assert data["last_name"] == user_data["last_name"]
        assert "id" in data
        assert "hashed_password" not in data
    
    async def test_register_duplicate_email(self, client: AsyncClient, test_user: User):
        """Test registration with duplicate email"""
        user_data = {
            "email": test_user.email,
            "password": "password123",
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = await client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]
    
    async def test_login_success(self, client: AsyncClient, test_user: User):
        """Test successful login"""
        login_data = {
            "username": test_user.email,
            "password": "testpassword123"
        }
        
        response = await client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
    
    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Test login with invalid credentials"""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = await client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    async def test_login_inactive_user(self, client: AsyncClient, db_session: AsyncSession):
        """Test login with inactive user"""
        # Create inactive user
        user = User(
            email="inactive@example.com",
            hashed_password="$2b$12$test",
            first_name="Inactive",
            last_name="User",
            is_active=False
        )
        db_session.add(user)
        await db_session.commit()
        
        login_data = {
            "username": user.email,
            "password": "password123"
        }
        
        response = await client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 400
        assert "Inactive user" in response.json()["detail"]
    
    async def test_get_current_user(self, client: AsyncClient, auth_headers: dict):
        """Test getting current user info"""
        response = await client.get("/api/v1/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "first_name" in data
        assert "last_name" in data
        assert "id" in data
    
    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        """Test getting current user without authentication"""
        response = await client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
    
    async def test_refresh_token(self, client: AsyncClient, test_user: User):
        """Test token refresh"""
        # First login to get tokens
        login_data = {
            "username": test_user.email,
            "password": "testpassword123"
        }
        
        login_response = await client.post("/api/v1/auth/login", data=login_data)
        tokens = login_response.json()
        
        # Refresh token
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_refresh_token_invalid(self, client: AsyncClient):
        """Test refresh with invalid token"""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )
        
        assert response.status_code == 401
        assert "Invalid refresh token" in response.json()["detail"]
    
    async def test_logout(self, client: AsyncClient, auth_headers: dict):
        """Test logout"""
        response = await client.post("/api/v1/auth/logout", headers=auth_headers)
        
        assert response.status_code == 200
        assert "Successfully logged out" in response.json()["message"]
