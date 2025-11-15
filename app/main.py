"""
Main application module for the Branch Loans API.

This module creates and configures the FastAPI application instance.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

# Import and include routers
try:
    from .routes import health as health_router
    app.include_router(health_router.router, prefix="/api", tags=["health"])
except ImportError:
    # If routes module is not available, just log a warning
    import logging
    logging.warning("Health router not found. Health check endpoint may not work as expected.")
