import sqlite3
from contextlib import contextmanager
from api.role_helpers import seed_default_roles

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

    conn.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            is_read INTEGER NOT NULL DEFAULT 0,
            board_id INTEGER,
            card_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (board_id) REFERENCES boards(id) ON DELETE SET NULL,
            FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE SET NULL
        )
    ''')

    notification_fields = _table_columns(conn, 'notifications')
    if 'board_id' not in notification_fields:
        conn.execute('ALTER TABLE notifications ADD COLUMN board_id INTEGER REFERENCES boards(id) ON DELETE SET NULL')
    if 'card_id' not in notification_fields:
        conn.execute('ALTER TABLE notifications ADD COLUMN card_id INTEGER REFERENCES cards(id) ON DELETE SET NULL')

    migrate_team_roles(conn)


def migrate_team_roles(conn):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS team_roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            slug TEXT NOT NULL,
            description TEXT,
            permissions TEXT NOT NULL DEFAULT '{}',
            is_system INTEGER NOT NULL DEFAULT 0,
            template_key TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
            UNIQUE(team_id, slug)
        )
    ''')

    teams = conn.execute('SELECT id FROM teams').fetchall()
    for team in teams:
        seed_default_roles(conn, team['id'])

    member_fields = _table_columns(conn, 'team_members')

    if 'role_id' not in member_fields:
        conn.execute('ALTER TABLE team_members ADD COLUMN role_id INTEGER REFERENCES team_roles(id)')

    if 'role' in member_fields:
        rows = conn.execute('SELECT team_id, user_id, role, role_id FROM team_members').fetchall()
        for row in rows:
            if row['role_id']:
                continue
            legacy_role = row['role'] or 'developer'
            role_row = conn.execute(
                'SELECT id FROM team_roles WHERE team_id = ? AND (template_key = ? OR slug = ?)',
                (row['team_id'], legacy_role, legacy_role)
            ).fetchone()
            if role_row:
                conn.execute(
                    'UPDATE team_members SET role_id = ? WHERE team_id = ? AND user_id = ?',
                    (role_row['id'], row['team_id'], row['user_id'])
                )
    else:
        _seed_default_members(conn)


def _seed_default_members(conn):
    """Начальные участники для чистой установки."""
    defaults = [
        (1, 1, 'developer'),
        (1, 2, 'developer'),
        (1, 3, 'leader'),
        (2, 5, 'leader'),
        (2, 1, 'developer'),
    ]
    for team_id, user_id, role_key in defaults:
        exists = conn.execute(
            'SELECT 1 FROM team_members WHERE team_id = ? AND user_id = ?',
            (team_id, user_id)
        ).fetchone()
        if exists:
            continue
        role_row = conn.execute(
            'SELECT id FROM team_roles WHERE team_id = ? AND template_key = ?',
            (team_id, role_key)
        ).fetchone()
        if role_row:
            conn.execute(
                'INSERT OR IGNORE INTO team_members (team_id, user_id, role_id) VALUES (?, ?, ?)',
                (team_id, user_id, role_row['id'])
            )

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
