"""
SecureFlow AI - Database Engine & Session Management
================================================================================
File: ai-service/app/db/session.py

Manages connection pooling, transactions, and engine initialization:
  - Supports PostgreSQL 17 via asyncpg/psycopg2
  - Transparent fallback to SQLite for offline edge environments or zero-dependency unit tests
  - Automatic idempotent table creation
"""

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.db.models import Base

logger = logging.getLogger("SecureFlowAI.Database")

# Determine Database Connection URL
# Priority: DATABASE_URL -> default local SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./secureflow_audit.db")

# For SQLite, ensure connect_args allows multi-threading
connect_args = {}
pool_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    # Production PostgreSQL connection pool settings
    pool_kwargs = {
        "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
        "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "20")),
        "pool_pre_ping": True,
        "pool_recycle": 1800,
    }

engine = create_engine(DATABASE_URL, connect_args=connect_args, **pool_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Idempotently initializes all database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info(f"[DB INIT] Database tables verified on '{DATABASE_URL.split('@')[-1]}'.")
    except Exception as e:
        logger.error(f"[DB INIT ERROR] Failed creating tables: {e}")


def get_db():
    """FastAPI Dependency for database session injection."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
