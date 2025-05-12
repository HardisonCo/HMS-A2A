"""
Error handling middleware for standardized API error responses.

This module provides consistent error handling and response formatting
across all agency API implementations.
"""

from datetime import datetime
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging
from typing import Dict, Any, Union


# Configure logging
logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware:
    """
    Middleware for standardized error handling.
    
    This class provides consistent error handling across agency APIs,
    ensuring uniform error response formatting and logging.
    """
    
    def __init__(self, app: FastAPI):
        """
        Initialize the middleware with a FastAPI application.
        
        Args:
            app: FastAPI application
        """
        self.app = app
        
        # Register exception handlers
        self._register_exception_handlers()
    
    def _register_exception_handlers(self):
        """Register exception handlers with the FastAPI application."""
        
        # Handle validation errors
        @self.app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc: RequestValidationError):
            return self._create_error_response(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                message="Validation error",
                detail=exc.errors(),
                path=request.url.path
            )
        
        # Handle SQLAlchemy errors
        @self.app.exception_handler(SQLAlchemyError)
        async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
            # Log the full error details
            logger.error(f"Database error: {str(exc)}", exc_info=True)
            
            return self._create_error_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Database error",
                detail="An error occurred while interacting with the database",
                path=request.url.path
            )
        
        # Handle general exceptions
        @self.app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            # Log the full error details
            logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
            
            return self._create_error_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Internal server error",
                detail=str(exc),
                path=request.url.path
            )
    
    @staticmethod
    def _create_error_response(status_code: int, message: str, detail: Union[str, list, Dict], path: str) -> JSONResponse:
        """
        Create a standardized error response.
        
        Args:
            status_code: HTTP status code
            message: Error message
            detail: Error details
            path: Request path
            
        Returns:
            JSON response with error details
        """
        return JSONResponse(
            status_code=status_code,
            content={
                "status": "error",
                "code": status_code,
                "message": message,
                "detail": detail,
                "path": path,
                "timestamp": datetime.now().isoformat()
            }
        )


def setup_error_handling(app: FastAPI) -> None:
    """
    Set up error handling for a FastAPI application.
    
    Args:
        app: FastAPI application
    """
    ErrorHandlingMiddleware(app)