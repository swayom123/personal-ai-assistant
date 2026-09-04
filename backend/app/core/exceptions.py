import logging
from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger("app.exceptions")

class AppException(Exception):
    """Base application exception."""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}

class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=status.HTTP_404_NOT_FOUND, details=details)

class ValidationException(AppException):
    def __init__(self, message: str = "Validation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, details=details)

# Phase 3 LLM Specific Exceptions
class AuthenticationException(AppException):
    """Raised when an API key is invalid or missing."""
    def __init__(self, message: str = "Invalid or missing LLM API credentials", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=status.HTTP_401_UNAUTHORIZED, details=details)

class ProviderUnavailableException(AppException):
    """Raised when an AI provider (e.g., Ollama server or OpenAI endpoint) is unreachable."""
    def __init__(self, message: str = "AI provider is currently unavailable or unreachable", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=status.HTTP_503_SERVICE_UNAVAILABLE, details=details)

class LLMTimeoutException(AppException):
    """Raised when a request to an LLM provider exceeds the configured timeout."""
    def __init__(self, message: str = "LLM provider request timed out", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=status.HTTP_504_GATEWAY_TIMEOUT, details=details)

class RateLimitException(AppException):
    """Raised when the LLM provider rate limit is exceeded."""
    def __init__(self, message: str = "LLM provider rate limit exceeded", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=status.HTTP_429_TOO_MANY_REQUESTS, details=details)

class ModelNotFoundException(AppException):
    """Raised when the requested model is not found on the provider."""
    def __init__(self, message: str = "Specified model is unavailable or not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=status.HTTP_404_NOT_FOUND, details=details)

class NetworkFailureException(AppException):
    """Raised on socket/DNS/network connectivity failure to the provider."""
    def __init__(self, message: str = "Network failure communicating with AI provider", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=status.HTTP_502_BAD_GATEWAY, details=details)

async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    logger.warning(f"AppException: {exc.message} (status: {exc.status_code}) [ReqID: {request_id}]")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.message,
                "status_code": exc.status_code,
                "details": exc.details,
                "request_id": request_id,
            }
        },
        headers={"X-Request-ID": request_id} if request_id else None
    )

async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    logger.error(f"Unhandled exception on {request.url.path} [ReqID: {request_id}]: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "message": "Internal server error",
                "status_code": 500,
                "request_id": request_id,
            }
        },
        headers={"X-Request-ID": request_id} if request_id else None
    )
