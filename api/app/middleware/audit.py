from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from app.models import AuditLog
from app.database import SessionLocal
from app.config import settings
import json
from datetime import datetime


class AuditLogMiddleware(BaseHTTPMiddleware):
    """Middleware for HIPAA-compliant audit logging"""
    
    async def dispatch(self, request: Request, call_next):
        # Skip audit logging for health checks
        if request.url.path in ["/health", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # Capture request details
        request_body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                request_body = body.decode("utf-8")
                # Store body for route handlers
                request._body = body
            except Exception:
                pass
        
        # Process request
        response = await call_next(request)
        
        # Log to audit trail if enabled
        if settings.AUDIT_LOG_ENABLED:
            try:
                db = SessionLocal()
                
                # Determine action from method and path
                action = f"{request.method} {request.url.path}"
                
                # Extract resource info from path
                path_parts = request.url.path.strip("/").split("/")
                resource_type = path_parts[0] if path_parts else None
                resource_id = path_parts[1] if len(path_parts) > 1 else None
                
                # Create audit log entry
                audit_entry = AuditLog(
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    user_id=request.headers.get("X-User-ID"),  # Set by auth middleware
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                    details={
                        "method": request.method,
                        "path": request.url.path,
                        "query_params": str(request.query_params),
                        "status_code": response.status_code,
                        "request_body_preview": request_body[:200] if request_body else None,
                    }
                )
                
                db.add(audit_entry)
                db.commit()
                db.close()
            except Exception as e:
                # Don't fail the request if audit logging fails
                print(f"Audit logging error: {e}")
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers for HIPAA compliance"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response
