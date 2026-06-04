"""Ролевая модель команды.

Куратор   — наблюдатель (teams.curator_id): просмотр + комментарии
Руководитель — team_members.role = leader: полное управление
Разработчик  — team_members.role = developer: работа только со своими задачами
"""


def get_user_role(conn, team_id, user_id):
    team = conn.execute(
        'SELECT curator_id FROM teams WHERE id = ?',
        (team_id,)
    ).fetchone()
    if not team:
        return 'none'

    if team['curator_id'] == user_id:
        return 'curator'

    member = conn.execute(
        'SELECT role FROM team_members WHERE team_id = ? AND user_id = ?',
        (team_id, user_id)
    ).fetchone()
    if member:
        return member['role']

    return 'none'


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
    role = get_user_role(conn, team_id, user_id)
    if role == 'none':
        return None, json_error('Access denied', 403)
    return role, None


def json_error(message, code):
    return message, code


def can_view(role):
    return role in ('curator', 'leader', 'developer')


def can_comment(role):
    return can_view(role)


def can_create_card(role):
    return role == 'leader'


def can_edit_card(role, card, user_id):
    if role == 'leader':
        return True
    if role == 'developer':
        return card['assignee_id'] == user_id
    return False


def can_delete_card(role):
    return role == 'leader'


def can_move_card(role, card, user_id):
    if role == 'leader':
        return True
    if role == 'developer':
        return card['assignee_id'] == user_id
    return False


def can_manage_columns(role):
    return role == 'leader'


def can_manage_board(role):
    return role == 'leader'


def can_assign(role):
    return role == 'leader'
