"""
API v1 Router Configuration
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, services, entities, documents, compliance

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(services.router, prefix="/services", tags=["services"])
api_router.include_router(entities.router, prefix="/entities", tags=["entities"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(compliance.router, prefix="/compliance", tags=["compliance"])
