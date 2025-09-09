"""
Custom Exception Classes
"""

from typing import Optional, Dict, Any


class LegalOpsException(Exception):
    """Base exception for Legal Ops Platform"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "LEGALOPS_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(LegalOpsException):
    """Validation error exception"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details=details
        )


class AuthenticationError(LegalOpsException):
    """Authentication error exception"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=401
        )


class AuthorizationError(LegalOpsException):
    """Authorization error exception"""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=403
        )


class NotFoundError(LegalOpsException):
    """Resource not found exception"""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            status_code=404
        )


class ConflictError(LegalOpsException):
    """Resource conflict exception"""
    
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(
            message=message,
            error_code="CONFLICT",
            status_code=409
        )


class RateLimitError(LegalOpsException):
    """Rate limit exceeded exception"""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429
        )


class ExternalServiceError(LegalOpsException):
    """External service error exception"""
    
    def __init__(self, message: str, service: str):
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=502,
            details={"service": service}
        )


class UPLComplianceError(LegalOpsException):
    """UPL compliance error exception"""
    
    def __init__(self, message: str = "UPL compliance violation"):
        super().__init__(
            message=message,
            error_code="UPL_COMPLIANCE_ERROR",
            status_code=422,
            details={"compliance_issue": "UPL"}
        )
