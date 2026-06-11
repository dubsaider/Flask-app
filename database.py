import sqlite3
from contextlib import contextmanager


_app_config = None


def init_app(app):
    """Привязать конфиг Flask к модулю БД."""
    global _app_config
    _app_config = app.config


def _cfg(key, default=None):
    if _app_config is not None:
        return _app_config.get(key, default)
    from config import get_config
    return getattr(get_config(), key, default)


def get_db():
    """Создает подключение к базе данных."""
    conn = sqlite3.connect(_cfg('DATABASE_PATH'))
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


@contextmanager
def get_db_context():
    """Контекстный менеджер для работы с БД."""
    conn = get_db()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
