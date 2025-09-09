"""
Custom Middleware Classes
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Request logging middleware"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }
        )
        
        # Process request
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"Response: {response.status_code} - {process_time:.4f}s",
            extra={
                "status_code": response.status_code,
                "process_time": process_time,
                "method": request.method,
                "path": request.url.path,
            }
        )
        
        # Add timing header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    def __init__(self, app, calls: int = 60, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.redis_client = None
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks
        if request.url.path == "/health":
            return await call_next(request)
        
        # Initialize Redis client if needed
        if not self.redis_client:
            try:
                self.redis_client = redis.from_url(settings.REDIS_URL)
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}")
                return await call_next(request)
        
        # Get client identifier
        client_ip = request.client.host if request.client else "unknown"
        key = f"rate_limit:{client_ip}"
        
        try:
            # Check current count
            current_count = await self.redis_client.get(key)
            
            if current_count is None:
                # First request in period
                await self.redis_client.setex(key, self.period, 1)
            else:
                current_count = int(current_count)
                if current_count >= self.calls:
                    # Rate limit exceeded
                    return JSONResponse(
                        status_code=429,
                        content={
                            "error": "RATE_LIMIT_EXCEEDED",
                            "message": f"Rate limit exceeded. Maximum {self.calls} requests per {self.period} seconds.",
                            "retry_after": self.period
                        },
                        headers={"Retry-After": str(self.period)}
                    )
                else:
                    # Increment counter
                    await self.redis_client.incr(key)
        
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Continue without rate limiting if Redis fails
        
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Security headers middleware"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Add HSTS header for HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response
