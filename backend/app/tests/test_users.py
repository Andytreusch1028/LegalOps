"""
User Management Tests
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestUserManagement:
    """Test user management endpoints"""
    
    async def test_get_current_user(self, client: AsyncClient, auth_headers: dict):
        """Test getting current user info"""
        response = await client.get("/api/v1/users/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "first_name" in data
        assert "last_name" in data
        assert "id" in data
        assert "roles" in data
    
    async def test_update_current_user(self, client: AsyncClient, auth_headers: dict):
        """Test updating current user info"""
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "company_name": "Updated Company"
        }
        
        response = await client.put(
            "/api/v1/users/me",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == update_data["first_name"]
        assert data["last_name"] == update_data["last_name"]
        assert data["company_name"] == update_data["company_name"]
    
    async def test_get_users_admin(self, client: AsyncClient, admin_auth_headers: dict):
        """Test getting all users as admin"""
        response = await client.get("/api/v1/users/", headers=admin_auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    async def test_get_users_non_admin(self, client: AsyncClient, auth_headers: dict):
        """Test getting all users as non-admin"""
        response = await client.get("/api/v1/users/", headers=auth_headers)
        
        assert response.status_code == 403
        assert "Insufficient permissions" in response.json()["detail"]
    
    async def test_get_user_by_id_admin(self, client: AsyncClient, admin_auth_headers: dict, test_user):
        """Test getting user by ID as admin"""
        response = await client.get(
            f"/api/v1/users/{test_user.id}",
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_user.id)
        assert data["email"] == test_user.email
    
    async def test_get_user_by_id_non_admin(self, client: AsyncClient, auth_headers: dict, test_user):
        """Test getting user by ID as non-admin"""
        response = await client.get(
            f"/api/v1/users/{test_user.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 403
        assert "Insufficient permissions" in response.json()["detail"]
    
    async def test_update_user_admin(self, client: AsyncClient, admin_auth_headers: dict, test_user):
        """Test updating user as admin"""
        update_data = {
            "first_name": "Admin Updated",
            "company_name": "Admin Updated Company"
        }
        
        response = await client.put(
            f"/api/v1/users/{test_user.id}",
            json=update_data,
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == update_data["first_name"]
        assert data["company_name"] == update_data["company_name"]
    
    async def test_activate_user_admin(self, client: AsyncClient, admin_auth_headers: dict, test_user):
        """Test activating user as admin"""
        response = await client.post(
            f"/api/v1/users/{test_user.id}/activate",
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        assert "activated successfully" in response.json()["message"]
    
    async def test_deactivate_user_admin(self, client: AsyncClient, admin_auth_headers: dict, test_user):
        """Test deactivating user as admin"""
        response = await client.post(
            f"/api/v1/users/{test_user.id}/deactivate",
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        assert "deactivated successfully" in response.json()["message"]
    
    async def test_add_user_role_admin(self, client: AsyncClient, admin_auth_headers: dict, test_user):
        """Test adding role to user as admin"""
        response = await client.post(
            f"/api/v1/users/{test_user.id}/roles/employee",
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        assert "Role 'employee' added" in response.json()["message"]
    
    async def test_remove_user_role_admin(self, client: AsyncClient, admin_auth_headers: dict, test_user):
        """Test removing role from user as admin"""
        # First add a role
        await client.post(
            f"/api/v1/users/{test_user.id}/roles/employee",
            headers=admin_auth_headers
        )
        
        # Then remove it
        response = await client.delete(
            f"/api/v1/users/{test_user.id}/roles/employee",
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        assert "Role 'employee' removed" in response.json()["message"]
