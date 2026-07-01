from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import sqlite3
from config import config

# Create engine
# connect_args is needed for SQLite to allow multiple threads
connect_args = {"check_same_thread": False} if config.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(config.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Read-Only engine
if config.DATABASE_URL.startswith("sqlite"):
    # Strip sqlite:/// to get the absolute path for the read-only file lock
    db_path = config.DATABASE_URL.replace("sqlite:///", "")
    creator = lambda: sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, check_same_thread=False)
    engine_ro = create_engine("sqlite:///", creator=creator)
else:
    engine_ro = engine # Fallback for Postgres/SQL Server where RO users should be configured externally

SessionLocalRO = sessionmaker(autocommit=False, autoflush=False, bind=engine_ro)

Base = declarative_base()

def get_db():
    """Returns a normal read/write database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_ro_db():
    """Returns a strictly Read-Only database session"""
    db = SessionLocalRO()
    try:
        yield db
    finally:
        db.close()
