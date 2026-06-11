"""Обёртка над SQLAlchemy session (замена sqlite3 get_db_context)."""
from contextlib import contextmanager

from extensions import db


@contextmanager
def session_scope():
    """Commit при успехе, rollback при ошибке."""
    try:
        yield db.session
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
