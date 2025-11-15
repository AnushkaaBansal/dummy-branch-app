"""
ASGI config for Branch Loans API.

This module contains the ASGI application used by FastAPI's development server and any
production ASGI deployments. It exposes a module-level variable named ``app``.
"""
import os
import logging
from typing import Any, Dict

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.db import init_db
from app.routes import health as health_router

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME if hasattr(settings, 'APP_NAME') else "Microloans API",
    description="A production-ready REST API for microloans",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS if hasattr(settings, 'BACKEND_CORS_ORIGINS') else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle global exceptions."""
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )

# Add startup event
@app.on_event("startup")
async def startup_event() -> None:
    """Run startup tasks."""
    logger.info("Starting up...")
    await init_db()
    logger.info("Database initialized")

# Add shutdown event
@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Run shutdown tasks."""
    logger.info("Shutting down...")

# Include API routes
app.include_router(health_router.router, prefix="/api", tags=["health"])

# Add Prometheus metrics
Instrumentator().instrument(app).expose(app)

# For Gunicorn
application = app
