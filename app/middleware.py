from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from typing import Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)


class APIKeyAuth(HTTPBearer):
    """API Key authentication for sensitive endpoints"""
    
    def __init__(self, auto_error: bool = True):
        super(APIKeyAuth, self).__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        return None

# API Key auth instance
api_key_auth = APIKeyAuth()

async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Custom rate limit exceeded handler"""
    response = _rate_limit_exceeded_handler(request, exc)
    logger.warning(f"Rate limit exceeded for {get_remote_address(request)}: {exc.detail}")
    return response

class SecurityHeaders:
    """Add security headers to responses"""
    
    @staticmethod
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self' https://maps.googleapis.com https://maps.gstatic.com https://fonts.googleapis.com https://fonts.gstatic.com https://cdn.jsdelivr.net https://cdn.tailwindcss.com; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://maps.googleapis.com https://cdn.jsdelivr.net https://cdn.tailwindcss.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://maps.googleapis.com https://maps.gstatic.com https://cdn.tailwindcss.com; "
            "style-src-elem 'self' 'unsafe-inline' https://fonts.googleapis.com https://maps.googleapis.com https://maps.gstatic.com https://cdn.tailwindcss.com; "
            "font-src 'self' https://fonts.gstatic.com https://maps.gstatic.com; "
            "img-src 'self' data: blob: https://maps.googleapis.com https://maps.gstatic.com https://*.googusercontent.com; "
            "connect-src 'self' https://maps.googleapis.com; "
            "worker-src blob:"
        )
        
        return response

async def log_requests(request: Request, call_next):
    """Log all requests for monitoring"""
    client_ip = get_remote_address(request)
    logger.info(f"Request: {request.method} {request.url.path} from {client_ip}")
    
    response = await call_next(request)
    
    logger.info(f"Response: {response.status_code} for {request.method} {request.url.path}")
    return response