"""Демо-данные для миграций."""
from sqlalchemy import text

from api.role_templates import ROLE_TEMPLATES, serialize_permissions


def seed_demo_data(conn):
    """Заполнить БД тестовыми данными (идемпотентно)."""
    conn.execute(text('''
        INSERT OR IGNORE INTO users (id, username, email, password_hash) VALUES
            (1, 'alice', 'alice@example.com', 'hash'),
            (2, 'bob', 'bob@example.com', 'hash'),
            (3, 'charlie', 'charlie@example.com', 'hash'),
            (4, 'diana', 'diana@example.com', 'hash'),
            (5, 'eve', 'eve@example.com', 'hash')
    '''))

    conn.execute(text('''
        INSERT OR IGNORE INTO teams (id, name, description, curator_id) VALUES
            (1, 'Development Team', 'Main development team', 4),
            (2, 'Design Team', 'UI/UX design team', NULL)
    '''))

    _seed_default_roles(conn, 1)
    _seed_default_roles(conn, 2)

    _seed_team_member(conn, 1, 1, 'developer')
    _seed_team_member(conn, 1, 2, 'developer')
    _seed_team_member(conn, 1, 3, 'leader')
    _seed_team_member(conn, 2, 5, 'leader')
    _seed_team_member(conn, 2, 1, 'developer')

    conn.execute(text('''
        INSERT OR IGNORE INTO boards (id, title, description, team_id) VALUES
            (1, 'Sprint 1', 'First sprint board', 1),
            (2, 'Design Tasks', 'Design related tasks', 2)
    '''))

    conn.execute(text('''
        INSERT OR IGNORE INTO columns (id, title, position, board_id, is_done) VALUES
            (1, 'To Do', 0, 1, 0),
            (2, 'In Progress', 1, 1, 0),
            (3, 'Review', 2, 1, 0),
            (4, 'Done', 3, 1, 1),
            (5, 'To Do', 0, 2, 0),
            (6, 'In Progress', 1, 2, 0),
            (7, 'Done', 2, 2, 1)
    '''))

    conn.execute(text('''
        INSERT OR IGNORE INTO cards
            (id, title, description, position, column_id, assignee_id, created_by, priority, status)
        VALUES
            (1, 'Setup project', 'Initialize repository and project structure', 0, 1, 1, 3, 'high', 'active'),
            (2, 'Design database', 'Create database schema', 1, 1, 2, 3, 'high', 'active'),
            (3, 'Implement API', 'Create REST API endpoints', 0, 2, 1, 3, 'medium', 'active'),
            (4, 'Write tests', 'Add unit tests', 0, 3, NULL, 3, 'low', 'active')
    '''))

    conn.execute(text('''
        INSERT OR IGNORE INTO comments (id, text, card_id, user_id) VALUES
            (1, 'Need to use PostgreSQL instead of SQLite', 1, 4),
            (2, 'I will start working on this today', 1, 1)
    '''))


def _seed_team_member(conn, team_id, user_id, role_key):
    role_row = conn.execute(
        text('SELECT id FROM team_roles WHERE team_id = :team_id AND template_key = :role_key'),
        {'team_id': team_id, 'role_key': role_key}
    ).fetchone()
    if not role_row:
        return
    conn.execute(
        text('''
            INSERT OR IGNORE INTO team_members (team_id, user_id, role_id)
            VALUES (:team_id, :user_id, :role_id)
        '''),
        {'team_id': team_id, 'user_id': user_id, 'role_id': role_row[0]}
    )


def _seed_default_roles(conn, team_id):
    existing = conn.execute(
        text('SELECT COUNT(*) AS cnt FROM team_roles WHERE team_id = :team_id'),
        {'team_id': team_id}
    ).scalar()
    if existing:
        return

    for template_key, template in ROLE_TEMPLATES.items():
        conn.execute(
            text('''
                INSERT INTO team_roles
                    (team_id, name, slug, description, permissions, is_system, template_key)
                VALUES
                    (:team_id, :name, :slug, :description, :permissions, :is_system, :template_key)
            '''),
            {
                'team_id': team_id,
                'name': template['name'],
                'slug': template_key,
                'description': template['description'],
                'permissions': serialize_permissions(template['permissions']),
                'is_system': 1 if template.get('is_system', True) else 0,
                'template_key': template_key,
            }
        )
