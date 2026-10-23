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
# Priority: DATABASE_URL -> data/secureflow_audit.db -> fallback
_ai_service_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_project_root = os.path.dirname(_ai_service_dir)
_data_db_path = os.path.join(_project_root, "data", "secureflow_audit.db")

if os.getenv("DATABASE_URL"):
    DATABASE_URL = os.getenv("DATABASE_URL")
elif os.path.exists(_data_db_path):
    DATABASE_URL = f"sqlite:///{_data_db_path.replace(os.sep, '/')}"
else:
    # Ensure data directory exists in project root
    os.makedirs(os.path.join(_project_root, "data"), exist_ok=True)
    DATABASE_URL = f"sqlite:///{_data_db_path.replace(os.sep, '/')}"



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
    """Idempotently initializes all database tables and ensures schema migrations."""
    try:
        Base.metadata.create_all(bind=engine)
        if DATABASE_URL.startswith("sqlite"):
            with engine.connect() as conn:
                from sqlalchemy import text
                res = conn.execute(text("PRAGMA table_info(dlp_incidents)")).fetchall()
                col_names = [r[1] for r in res]
                if col_names and "prev_hash" not in col_names:
                    conn.execute(text("ALTER TABLE dlp_incidents ADD COLUMN prev_hash VARCHAR(64) DEFAULT 'GENESIS_BLOCK_0000000000000000000000000000000000000000000000000000'"))
                if col_names and "audit_hash" not in col_names:
                    conn.execute(text("ALTER TABLE dlp_incidents ADD COLUMN audit_hash VARCHAR(64)"))
                if col_names and "compliance_tags" not in col_names:
                    conn.execute(text("ALTER TABLE dlp_incidents ADD COLUMN compliance_tags JSON"))
                if col_names and "threat_category" not in col_names:
                    conn.execute(text("ALTER TABLE dlp_incidents ADD COLUMN threat_category VARCHAR(128) DEFAULT 'BENIGN_DATA'"))
                if col_names and "explanation" not in col_names:
                    conn.execute(text("ALTER TABLE dlp_incidents ADD COLUMN explanation TEXT"))
                if col_names and "remediation_advice" not in col_names:
                    conn.execute(text("ALTER TABLE dlp_incidents ADD COLUMN remediation_advice TEXT"))
                conn.commit()
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
