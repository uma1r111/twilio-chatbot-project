"""
Database engine and session setup using SQLAlchemy + SQLite.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./database.db"

# check_same_thread=False is needed because FastAPI can use multiple
# threads, while SQLite by default only allows one thread per connection.
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency that yields a DB session and ensures it's closed
    after the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()