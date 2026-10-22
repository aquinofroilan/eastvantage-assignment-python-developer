"""Database dependencies for API routes."""

from collections.abc import Generator

from sqlalchemy.orm import Session

from app.models import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Provide a database session for the lifetime of one request.

    Yields:
        A SQLAlchemy database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
