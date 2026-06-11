"""Ролевая модель команды с настраиваемыми правами."""
from labels import ROLE_LABELS

from models.orm_utils import attr
from models.schema import Board, Card, Column, Team, TeamMember, TeamRole
from .role_templates import normalize_permissions, permissions_from_template, serialize_permissions
from .role_helpers import get_team_role_by_slug


def get_user_role_row(session, team_id, user_id):
    team = session.get(Team, team_id)
    if not team:
        return None

    if team.curator_id == user_id:
        curator_role = get_team_role_by_slug(session, team_id, 'curator')
        return curator_role or _virtual_curator_role(team_id)

    member = (
        session.query(TeamRole)
        .join(TeamMember, TeamMember.role_id == TeamRole.id)
        .filter(TeamMember.team_id == team_id, TeamMember.user_id == user_id)
        .first()
    )
    return member


def _virtual_curator_role(team_id):
    return {
        'id': None,
        'team_id': team_id,
        'name': ROLE_LABELS['curator'],
        'slug': 'curator',
        'description': '',
        'permissions': serialize_permissions(permissions_from_template('curator')),
        'is_system': True,
        'template_key': 'curator',
    }


def _role_slug(row):
    if isinstance(row, dict):
        return row['slug']
    return row.slug


def _role_name(row):
    if isinstance(row, dict):
        return row['name']
    return row.name


def _role_id(row):
    if isinstance(row, dict):
        return row['id']
    return row.id


def _role_permissions(row):
    if isinstance(row, dict):
        perms = row['permissions']
    else:
        perms = row.permissions
    return normalize_permissions(perms)


def get_user_role(session, team_id, user_id):
    row = get_user_role_row(session, team_id, user_id)
    if not row:
        return 'none'
    return _role_slug(row)


def get_user_permissions(session, team_id, user_id):
    row = get_user_role_row(session, team_id, user_id)
    if not row:
        return normalize_permissions(None)
    return _role_permissions(row)


def get_user_role_info(session, team_id, user_id):
    row = get_user_role_row(session, team_id, user_id)
    if not row:
        return {
            'slug': 'none',
            'name': '',
            'role_id': None,
            'permissions': normalize_permissions(None),
        }
    return {
        'slug': _role_slug(row),
        'name': _role_name(row),
        'role_id': _role_id(row),
        'permissions': _role_permissions(row),
    }


def get_team_id_for_board(session, board_id):
    board = session.get(Board, board_id)
    return board.team_id if board else None


def get_team_id_for_column(session, column_id):
    row = (
        session.query(Board.team_id)
        .join(Column, Column.board_id == Board.id)
        .filter(Column.id == column_id)
        .first()
    )
    return row[0] if row else None


def get_team_id_for_card(session, card_id):
    row = (
        session.query(Board.team_id)
        .join(Column, Column.board_id == Board.id)
        .join(Card, Card.column_id == Column.id)
        .filter(Card.id == card_id)
        .first()
    )
    return row[0] if row else None


def get_card(session, card_id):
    return session.get(Card, card_id)


def check_access(session, team_id, user_id):
    perms = get_user_permissions(session, team_id, user_id)
    if not perms.get('view_board'):
        return None, ('Access denied', 403)
    return get_user_role_info(session, team_id, user_id), None


def _perms(session, team_id, user_id):
    return get_user_permissions(session, team_id, user_id)


def can_view(session, team_id, user_id):
    return _perms(session, team_id, user_id).get('view_board', False)


def can_comment(session, team_id, user_id):
    return _perms(session, team_id, user_id).get('comment', False)


def can_create_card(session, team_id, user_id):
    return _perms(session, team_id, user_id).get('create_card', False)


def can_edit_card(session, team_id, user_id, card=None):
    return _perms(session, team_id, user_id).get('edit_card', False)


def can_delete_card(session, team_id, user_id):
    return _perms(session, team_id, user_id).get('delete_card', False)


def can_move_card(session, team_id, user_id, card):
    perms = _perms(session, team_id, user_id)
    if perms.get('move_card'):
        return True
    assignee_id = attr(card, 'assignee_id')
    if perms.get('move_card_own_only') and card and assignee_id == user_id:
        return True
    return False


def can_manage_columns(session, team_id, user_id):
    return _perms(session, team_id, user_id).get('manage_columns', False)


def can_manage_board(session, team_id, user_id):
    return _perms(session, team_id, user_id).get('manage_board', False)


def can_assign(session, team_id, user_id):
    return _perms(session, team_id, user_id).get('assign_card', False)


def can_archive(session, team_id, user_id):
    return _perms(session, team_id, user_id).get('archive_card', False)


def can_manage_team_members(session, team_id, user_id):
    return _perms(session, team_id, user_id).get('manage_team_members', False)


def can_manage_roles(session, team_id, user_id):
    return _perms(session, team_id, user_id).get('manage_roles', False)


def can_view_dashboard(session, team_id, user_id):
    return _perms(session, team_id, user_id).get('view_dashboard', False)
