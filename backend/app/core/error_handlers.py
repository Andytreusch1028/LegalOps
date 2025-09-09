"""
Global Error Handlers and Middleware
"""

import logging
import traceback
from typing import Union
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError

from app.core.exceptions import LegalOpsException
from app.core.config import settings

logger = logging.getLogger(__name__)


async def legalops_exception_handler(request: Request, exc: LegalOpsException) -> JSONResponse:
    """Handle custom Legal Ops exceptions"""
    logger.error(f"LegalOps Exception: {exc.error_code} - {exc.message}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "details": exc.details,
            "timestamp": exc.timestamp if hasattr(exc, 'timestamp') else None
        }
    )


async def http_exception_handler(request: Request, exc: Union[HTTPException, StarletteHTTPException]) -> JSONResponse:
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP_ERROR",
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors"""
    logger.warning(f"Validation Error: {exc.errors()}")
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": exc.errors()
        }
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle SQLAlchemy database errors"""
    logger.error(f"Database Error: {str(exc)}")
    
    if isinstance(exc, IntegrityError):
        return JSONResponse(
            status_code=409,
            content={
                "error": "DATABASE_CONFLICT",
                "message": "Database integrity constraint violation",
                "details": "The operation conflicts with existing data"
            }
        )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "DATABASE_ERROR",
            "message": "Database operation failed",
            "details": str(exc) if settings.ENVIRONMENT == "development" else None
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions"""
    logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
    
    # Log full traceback for debugging
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An internal server error occurred",
            "details": str(exc) if settings.ENVIRONMENT == "development" else None,
            "request_id": getattr(request.state, 'request_id', None)
        }
    )


def setup_error_handlers(app):
    """Setup all error handlers for the FastAPI app"""
    app.add_exception_handler(LegalOpsException, legalops_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
