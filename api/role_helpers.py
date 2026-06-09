"""Создание и загрузка ролей команды."""
import json
from .role_templates import ROLE_TEMPLATES, serialize_permissions, normalize_permissions


def seed_default_roles(conn, team_id):
    """Создать встроенные роли команды из шаблонов."""
    existing = conn.execute(
        'SELECT COUNT(*) AS cnt FROM team_roles WHERE team_id = ?',
        (team_id,)
    ).fetchone()['cnt']
    if existing:
        return

    for template_key, template in ROLE_TEMPLATES.items():
        conn.execute(
            '''INSERT INTO team_roles
               (team_id, name, slug, description, permissions, is_system, template_key)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (
                team_id,
                template['name'],
                template_key,
                template['description'],
                serialize_permissions(template['permissions']),
                1 if template.get('is_system', True) else 0,
                template_key,
            )
        )


def get_team_role_by_slug(conn, team_id, slug):
    return conn.execute(
        'SELECT * FROM team_roles WHERE team_id = ? AND slug = ?',
        (team_id, slug)
    ).fetchone()


def get_team_role_by_id(conn, team_id, role_id):
    return conn.execute(
        'SELECT * FROM team_roles WHERE team_id = ? AND id = ?',
        (team_id, role_id)
    ).fetchone()


def load_team_roles(conn, team_id):
    rows = conn.execute(
        'SELECT * FROM team_roles WHERE team_id = ? ORDER BY is_system DESC, name',
        (team_id,)
    ).fetchall()
    return [role_row_to_dict(row) for row in rows]


def role_row_to_dict(row):
    return {
        'id': row['id'],
        'team_id': row['team_id'],
        'name': row['name'],
        'slug': row['slug'],
        'description': row['description'],
        'permissions': normalize_permissions(row['permissions']),
        'is_system': bool(row['is_system']),
        'template_key': row['template_key'],
    }


def unique_slug(conn, team_id, base_slug):
    slug = base_slug
    index = 2
    while conn.execute(
        'SELECT 1 FROM team_roles WHERE team_id = ? AND slug = ?',
        (team_id, slug)
    ).fetchone():
        slug = f'{base_slug}-{index}'
        index += 1
    return slug


def count_members_with_role(conn, role_id):
    return conn.execute(
        'SELECT COUNT(*) AS cnt FROM team_members WHERE role_id = ?',
        (role_id,)
    ).fetchone()['cnt']
