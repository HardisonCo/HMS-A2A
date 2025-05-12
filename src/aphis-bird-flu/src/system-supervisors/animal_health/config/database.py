"""
Database configuration and connection management for the APHIS Bird Flu Tracking System.

This module provides functionality for database connection, session management,
and ORM configuration using SQLAlchemy with PostgreSQL and PostGIS.
"""

import os
import logging
from typing import Generator, Optional
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from geoalchemy2 import load_spatialite

# Configure logging
logger = logging.getLogger(__name__)

# Base class for ORM models
Base = declarative_base()

# Get database connection parameters from environment variables
DB_HOST = os.getenv("APHIS_DB_HOST", "localhost")
DB_PORT = os.getenv("APHIS_DB_PORT", "5432")
DB_NAME = os.getenv("APHIS_DB_NAME", "aphis_bird_flu")
DB_USER = os.getenv("APHIS_DB_USER", "postgres")
DB_PASSWORD = os.getenv("APHIS_DB_PASSWORD", "postgres")

# Construct connection URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine with appropriate pool settings
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_recycle=300,  # Recycle connections after 5 minutes
    pool_pre_ping=True,  # Check connection health before using
    pool_use_lifo=True,  # LIFO pool for better locality
    echo=os.getenv("APHIS_DB_ECHO", "false").lower() == "true",  # SQL echo for debugging
)

# Initialize sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize GIS extension
@event.listens_for(engine, "connect")
def _connect(dbapi_connection, conn_record):
    """
    Initialize spatial extensions on connection.

    This is a SQLAlchemy event that is triggered when a new connection
    is made to the database. It enables the PostGIS extension for spatial
    functionality.
    """
    # PostgreSQL doesn't need explicit load like SQLite does
    # with PostGIS, the extension is enabled at the database level
    pass

def get_db() -> Generator[Session, None, None]:
    """
    Get a database session.

    This function provides a session from the session pool and
    ensures it is properly closed after use. It is designed to
    be used as a FastAPI dependency.

    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.

    This context manager provides a session and handles
    commit/rollback based on exceptions.

    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        db.close()

def init_db() -> None:
    """
    Initialize the database.

    Creates all tables defined in the ORM models.
    """
    try:
        # Create all tables if they don't exist
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

def check_connection() -> bool:
    """
    Check database connection.

    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        # Try executing a simple query
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return False

def execute_script(script_path: str) -> None:
    """
    Execute a SQL script.

    Args:
        script_path: Path to the SQL script file
    """
    try:
        with open(script_path, 'r') as file:
            sql = file.read()
        
        with engine.begin() as conn:
            conn.execute(sql)
        
        logger.info(f"Successfully executed script: {script_path}")
    except Exception as e:
        logger.error(f"Error executing script {script_path}: {str(e)}")
        raise