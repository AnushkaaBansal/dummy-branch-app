"""Database configuration and session management.

This module provides database connection, session management, and initialization
utilities for the Branch Loans API.
"""
import logging
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine, event
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, scoped_session, Session as SessionType, declarative_base
from sqlalchemy.pool import QueuePool

# Create a declarative base class for models
Base = declarative_base()

from .config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create database engine with connection pooling
engine = create_engine(
    str(settings.DATABASE_URL),
    poolclass=QueuePool,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    pool_pre_ping=settings.DATABASE_POOL_PRE_PING,
    pool_recycle=settings.DATABASE_POOL_RECYCLE,
    echo=settings.SQL_ECHO,
    echo_pool=settings.SQL_ECHO_POOL,
)

# Create a scoped session factory
SessionFactory = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        expire_on_commit=False,  # Prevent detached instance errors
    )
)

# Type alias for database session
Session = SessionType

# Dependency to get database session
@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Get a database session with automatic cleanup.
    
    Yields:
        Session: A SQLAlchemy database session
        
    Example:
        with get_db() as db:
            db.query(User).all()
    """
    session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        session.close()


def init_db() -> None:
    """Initialize the database by creating all tables.
    
    This should be called during application startup.
    """
    from . import models  # noqa: F401
    
    try:
        # Import all models here to ensure they are registered with SQLAlchemy
        from .models import Base
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def close_db() -> None:
    """Close the database connection."""
    SessionFactory.remove()
    engine.dispose()
    logger.info("Database connections closed")


# Add database connection event listeners
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign key constraints for SQLite."""
    if "sqlite" in str(dbapi_connection.engine.url):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# Add connection pool event listeners
@event.listens_for(engine, "checkout")
def on_checkout(dbapi_connection, connection_record, connection_proxy):
    """Log when a connection is checked out from the pool."""
    logger.debug("Connection checked out from pool")


@event.listens_for(engine, "checkin")
def on_checkin(dbapi_connection, connection_record):
    """Log when a connection is returned to the pool."""
    logger.debug("Connection returned to pool")


# Add error handling for database operations
def handle_database_error(e: Exception) -> None:
    """Handle database errors and log them appropriately.
    
    Args:
        e: The exception that was raised
        
    Raises:
        HTTPException: A 500 error with a generic message
    """
    from fastapi import HTTPException, status
    
    logger.error(f"Database error: {e}")
    
    if isinstance(e, SQLAlchemyError):
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="A database error occurred",
        ) from e
    raise e

# Simple context manager for sessions
class SessionContext:
    def __enter__(self):
        self.session = SessionFactory()
        return self.session

    def __exit__(self, exc_type, exc, tb):
        try:
            if exc_type is None:
                self.session.commit()
            else:
                self.session.rollback()
        finally:
            self.session.close()
