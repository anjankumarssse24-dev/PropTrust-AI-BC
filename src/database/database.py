"""
Database Configuration
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./data/proptrust.db"  # Default to SQLite
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Get database session
    
    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database (create all tables)"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized")


def drop_db():
    """Drop all tables (use with caution!)"""
    Base.metadata.drop_all(bind=engine)
    print("⚠️  Database dropped")
