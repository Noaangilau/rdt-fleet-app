"""
database.py — SQLAlchemy engine and session setup.

Reads DATABASE_URL from environment. Defaults to a local SQLite file (fleet.db).
To switch to PostgreSQL on Railway/Render, set DATABASE_URL to your postgres:// URL
and this file handles the rest with zero code changes.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Read database URL from environment, default to local SQLite file
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./fleet.db")

# Railway and some providers use postgres:// but SQLAlchemy requires postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite needs check_same_thread=False for FastAPI's async request handling
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Each request gets its own database session via the get_db dependency
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All ORM models inherit from this Base
Base = declarative_base()


def get_db():
    """FastAPI dependency that provides a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
