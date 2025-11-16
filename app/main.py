"""
Main application module for the Branch Loans API.

This module creates and configures the FastAPI application instance.
"""
import logging
import sys
import traceback
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
import uuid
from app.metrics import PrometheusMiddleware, get_metrics_route

# Configure structured logging first
logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "request_id": "%(request_id)s"}',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Branch Loans API",
    description="API for managing microloans",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Log request
    logger.info(
        "Request started",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params)
        }
    )
    
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(
            "Request failed",
            extra={
                "request_id": request_id,
                "error": str(e),
                "traceback": str(traceback.format_exc())
            }
        )
        raise HTTPException(status_code=500, detail="Internal server error")
    
    # Calculate processing time
    process_time = (time.time() - start_time) * 1000
    
    # Log response
    logger.info(
        "Request completed",
        extra={
            "request_id": request_id,
            "status_code": response.status_code,
            "process_time_ms": process_time
        }
    )
    
    # Add request ID to response headers
    response.headers["X-Request-ID"] = request_id
    return response

# Import and include routers
try:
    from app.routes import health as health_router
    app.include_router(health_router.router, prefix="/api", tags=["health"])
except ImportError as e:
    logger.warning(f"Failed to import health router: {str(e)}. Health check endpoint may not work as expected.")


# Add Prometheus metrics endpoint
app.add_route("/metrics", get_metrics_route())

# Add Prometheus middleware
app.add_middleware(PrometheusMiddleware)