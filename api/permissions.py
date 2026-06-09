"""Ролевая модель команды с настраиваемыми правами."""
from .role_templates import normalize_permissions, permissions_from_template
from .role_helpers import get_team_role_by_slug


def get_user_role_row(conn, team_id, user_id):
    """Возвращает строку team_roles для пользователя или None."""
    team = conn.execute(
        'SELECT curator_id FROM teams WHERE id = ?',
        (team_id,)
    ).fetchone()
    if not team:
        return None

    if team['curator_id'] == user_id:
        curator_role = get_team_role_by_slug(conn, team_id, 'curator')
        return curator_role or _virtual_curator_role(team_id)

    member = conn.execute('''
        SELECT tr.*
        FROM team_members tm
        JOIN team_roles tr ON tm.role_id = tr.id
        WHERE tm.team_id = ? AND tm.user_id = ?
    ''', (team_id, user_id)).fetchone()
    if member:
        return member

    return None


def _virtual_curator_role(team_id):
    """Fallback, если роль куратора ещё не создана."""
    from .role_templates import serialize_permissions
    return {
        'id': None,
        'team_id': team_id,
        'name': 'Куратор',
        'slug': 'curator',
        'description': '',
        'permissions': serialize_permissions(permissions_from_template('curator')),
        'is_system': 1,
        'template_key': 'curator',
    }


def get_user_role(conn, team_id, user_id):
    row = get_user_role_row(conn, team_id, user_id)
    if not row:
        return 'none'
    return row['slug'] if isinstance(row, dict) or hasattr(row, 'keys') else row.slug


def get_user_permissions(conn, team_id, user_id):
    row = get_user_role_row(conn, team_id, user_id)
    if not row:
        return normalize_permissions(None)
    perms = row['permissions']
    if isinstance(perms, str):
        return normalize_permissions(perms)
    return normalize_permissions(perms)


def get_user_role_info(conn, team_id, user_id):
    row = get_user_role_row(conn, team_id, user_id)
    if not row:
        return {
            'slug': 'none',
            'name': '',
            'role_id': None,
            'permissions': normalize_permissions(None),
        }
    return {
        'slug': row['slug'],
        'name': row['name'],
        'role_id': row['id'],
        'permissions': get_user_permissions(conn, team_id, user_id),
    }


def get_team_id_for_board(conn, board_id):
    row = conn.execute(
        'SELECT team_id FROM boards WHERE id = ?',
        (board_id,)
    ).fetchone()
    return row['team_id'] if row else None


def get_team_id_for_column(conn, column_id):
    row = conn.execute('''
        SELECT b.team_id FROM columns c
        JOIN boards b ON c.board_id = b.id
        WHERE c.id = ?
    ''', (column_id,)).fetchone()
    return row['team_id'] if row else None


def get_team_id_for_card(conn, card_id):
    row = conn.execute('''
        SELECT b.team_id FROM cards c
        JOIN columns col ON c.column_id = col.id
        JOIN boards b ON col.board_id = b.id
        WHERE c.id = ?
    ''', (card_id,)).fetchone()
    return row['team_id'] if row else None


def get_card(conn, card_id):
    return conn.execute('SELECT * FROM cards WHERE id = ?', (card_id,)).fetchone()


def check_access(conn, team_id, user_id):
    perms = get_user_permissions(conn, team_id, user_id)
    if not perms.get('view_board'):
        return None, json_error('Access denied', 403)
    role_info = get_user_role_info(conn, team_id, user_id)
    return role_info, None


def json_error(message, code):
    return message, code


def _perms(conn, team_id, user_id):
    return get_user_permissions(conn, team_id, user_id)


def can_view(conn, team_id, user_id):
    return _perms(conn, team_id, user_id).get('view_board', False)


def can_comment(conn, team_id, user_id):
    return _perms(conn, team_id, user_id).get('comment', False)


def can_create_card(conn, team_id, user_id):
    return _perms(conn, team_id, user_id).get('create_card', False)


def can_edit_card(conn, team_id, user_id, card=None):
    return _perms(conn, team_id, user_id).get('edit_card', False)


def can_delete_card(conn, team_id, user_id):
    return _perms(conn, team_id, user_id).get('delete_card', False)


def can_move_card(conn, team_id, user_id, card):
    perms = _perms(conn, team_id, user_id)
    if perms.get('move_card'):
        return True
    if perms.get('move_card_own_only') and card and card['assignee_id'] == user_id:
        return True
    return False


def can_manage_columns(conn, team_id, user_id):
    return _perms(conn, team_id, user_id).get('manage_columns', False)


def can_manage_board(conn, team_id, user_id):
    return _perms(conn, team_id, user_id).get('manage_board', False)


def can_assign(conn, team_id, user_id):
    return _perms(conn, team_id, user_id).get('assign_card', False)


def can_archive(conn, team_id, user_id):
    return _perms(conn, team_id, user_id).get('archive_card', False)


def can_manage_team_members(conn, team_id, user_id):
    return _perms(conn, team_id, user_id).get('manage_team_members', False)


def can_manage_roles(conn, team_id, user_id):
    return _perms(conn, team_id, user_id).get('manage_roles', False)


def can_view_dashboard(conn, team_id, user_id):
    return _perms(conn, team_id, user_id).get('view_dashboard', False)
