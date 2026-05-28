import sqlite3
from contextlib import contextmanager

DATABASE = 'kanban.db'

def get_db():
    """Создает подключение к базе данных"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Чтобы получать результаты как словари
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Инициализация базы данных из schema.sql"""
    with get_db() as conn:
        with open('schema.sql', 'r') as f:
            conn.executescript(f.read())
        conn.commit()

@contextmanager
def get_db_context():
    """Контекстный менеджер для работы с БД"""
    conn = get_db()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()