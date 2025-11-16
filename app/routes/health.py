import logging
import time
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from sqlalchemy import text
import json
from datetime import datetime

# Configure JSON logging
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if hasattr(record, 'extra'):
            log_record.update(record.extra)
        return json.dumps(log_record)

logger = logging.getLogger("api.health")
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

router = APIRouter()

def get_uptime() -> float:
    """Returns the uptime of the application in seconds"""
    return time.time() - get_uptime.start_time

# Initialize the start time when the module loads
get_uptime.start_time = time.time()

def check_database(db: Session) -> Dict[str, Any]:
    """Check database connection and return status"""
    start_time = time.time()
    try:
        db.execute(text("SELECT 1"))
        db_status = "healthy"
        error = None
    except Exception as e:
        db_status = "unhealthy"
        error = str(e)
        logger.error("Database health check failed", extra={"error": str(e)})
    
    return {
        "status": db_status,
        "latency_ms": round((time.time() - start_time) * 1000, 2),
        "error": error
    }

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check endpoint"""
    start_time = time.time()
    checks = {}
    
    # Check database
    db_check = check_database(db)
    checks["database"] = db_check
    
    # Add more checks here (e.g., cache, external services)
    
    # Overall status
    all_healthy = all(check["status"] == "healthy" for check in checks.values())
    status = "healthy" if all_healthy else "unhealthy"
    
    # Prepare response
    response = {
        "status": status,
        "version": "1.0.0",  # Consider loading from package.json or similar
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "uptime_seconds": round(get_uptime(), 2),
        "checks": checks,
        "latency_ms": round((time.time() - start_time) * 1000, 2)
    }
    
    # Log the health check
    log_extra = {
        "status": status,
        "latency_ms": response["latency_ms"],
        "checks": checks
    }
    logger.info("Health check performed", extra=log_extra)
    
    if status != "healthy":
        raise HTTPException(
            status_code=503,
            detail=response,
            headers={"Retry-After": "30"}  # Suggest when to retry
        )
    
    return response

@router.get("/health/liveness")
async def liveness_probe():
    """Kubernetes liveness probe endpoint"""
    return {"status": "alive"}

@router.get("/health/readiness")
async def readiness_probe(db: Session = Depends(get_db)):
    """Kubernetes readiness probe endpoint"""
    db_check = check_database(db)
    if db_check["status"] != "healthy":
        raise HTTPException(
            status_code=503,
            detail={"status": "not ready", "database": db_check}
        )
    return {"status": "ready"}