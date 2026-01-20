"""
Error Handling Middleware
Comprehensive error handling for the OSF Demo API
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import structlog
import traceback
from typing import Callable

logger = structlog.get_logger()


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Global error handling middleware."""
    
    async def dispatch(self, request: Request, call_next: Callable):
        try:
            response = await call_next(request)
            return response
        
        except HTTPException as e:
            # Pass through HTTP exceptions
            logger.warning("http_exception",
                          path=request.url.path,
                          status=e.status_code,
                          detail=e.detail)
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": True,
                    "message": e.detail,
                    "status_code": e.status_code,
                }
            )
        
        except ValueError as e:
            # Validation errors
            logger.warning("validation_error",
                          path=request.url.path,
                          error=str(e))
            return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "message": str(e),
                    "status_code": 400,
                    "error_type": "validation",
                }
            )
        
        except ConnectionError as e:
            # Database or external service connection errors
            logger.error("connection_error",
                        path=request.url.path,
                        error=str(e))
            return JSONResponse(
                status_code=503,
                content={
                    "error": True,
                    "message": "Service temporarily unavailable",
                    "status_code": 503,
                    "error_type": "connection",
                }
            )
        
        except Exception as e:
            # Unexpected errors
            error_id = id(e)  # Unique identifier for this error
            logger.error("unhandled_exception",
                        path=request.url.path,
                        error=str(e),
                        error_type=type(e).__name__,
                        error_id=error_id,
                        traceback=traceback.format_exc())
            
            return JSONResponse(
                status_code=500,
                content={
                    "error": True,
                    "message": "An unexpected error occurred",
                    "status_code": 500,
                    "error_type": "internal",
                    "error_id": error_id,
                }
            )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests for debugging."""
    
    async def dispatch(self, request: Request, call_next: Callable):
        import time
        
        start_time = time.time()
        
        # Log request
        logger.debug("request_started",
                    method=request.method,
                    path=request.url.path,
                    query=str(request.query_params))
        
        response = await call_next(request)
        
        # Log response
        duration_ms = int((time.time() - start_time) * 1000)
        logger.debug("request_completed",
                    method=request.method,
                    path=request.url.path,
                    status=response.status_code,
                    duration_ms=duration_ms)
        
        # Add timing header
        response.headers["X-Response-Time"] = f"{duration_ms}ms"
        
        return response


def setup_error_handlers(app):
    """Setup exception handlers for the FastAPI app."""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.detail,
                "status_code": exc.status_code,
            }
        )
    
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        logger.warning("validation_error", error=str(exc))
        return JSONResponse(
            status_code=400,
            content={
                "error": True,
                "message": str(exc),
                "status_code": 400,
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error("unhandled_exception",
                    error=str(exc),
                    error_type=type(exc).__name__,
                    traceback=traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "Internal server error",
                "status_code": 500,
            }
        )
