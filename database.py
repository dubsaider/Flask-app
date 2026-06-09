import sqlite3
from contextlib import contextmanager

DATABASE = 'kanban.db'

def get_db():
    """Создает подключение к базе данных"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def _table_columns(conn, table_name):
    return {row[1] for row in conn.execute(f'PRAGMA table_info({table_name})').fetchall()}

def migrate_db(conn):
    """Миграции для существующей базы"""
    column_fields = _table_columns(conn, 'columns')
    if 'is_done' not in column_fields:
        conn.execute('ALTER TABLE columns ADD COLUMN is_done INTEGER NOT NULL DEFAULT 0')
        conn.execute('''
            UPDATE columns SET is_done = 1
            WHERE lower(trim(title)) IN ('done', 'готово', 'closed', 'complete', 'completed')
        ''')

    conn.execute("UPDATE cards SET status = 'active' WHERE status = 'completed'")

def init_db():
    """Инициализация базы данных из schema.sql"""
    with get_db() as conn:
        with open('schema.sql', 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        migrate_db(conn)
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
