"""Database session management utilities"""

from contextlib import contextmanager
from typing import Generator
from sqlalchemy.orm import Session
from app.database import db


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.

    Ensures proper commit/rollback and session cleanup.

    Usage:
        with get_db_session() as session:
            user = session.query(User).filter_by(id=1).first()
            session.add(user)
            # Automatic commit on success, rollback on exception
    """
    session = db.session
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def save_to_db(obj) -> None:
    """
    Save an object to the database.

    Args:
        obj: SQLAlchemy model instance to save

    Raises:
        Exception: If database operation fails
    """
    try:
        db.session.add(obj)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def delete_from_db(obj) -> None:
    """
    Delete an object from the database.

    Args:
        obj: SQLAlchemy model instance to delete

    Raises:
        Exception: If database operation fails
    """
    try:
        db.session.delete(obj)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def commit_db() -> None:
    """
    Commit the current database session.

    Raises:
        Exception: If commit fails
    """
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def rollback_db() -> None:
    """Rollback the current database session."""
    db.session.rollback()
