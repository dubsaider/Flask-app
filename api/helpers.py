from models import User, Team
from database import get_db_context


def load_team(conn, team_row):
    team_obj = Team(team_row)
    members = conn.execute('''
        SELECT u.*, tm.role
        FROM users u
        JOIN team_members tm ON u.id = tm.user_id
        WHERE tm.team_id = ?
    ''', (team_obj.id,)).fetchall()
    team_obj.members = [User(m) for m in members]
    if team_obj.curator_id:
        curator = conn.execute(
            'SELECT * FROM users WHERE id = ?',
            (team_obj.curator_id,)
        ).fetchone()
        if curator:
            team_obj.curator = User(curator)
    return team_obj


def user_has_team_access(conn, team_row, user_id):
    if team_row['curator_id'] == user_id:
        return True
    member = conn.execute(
        'SELECT 1 FROM team_members WHERE team_id = ? AND user_id = ?',
        (team_row['id'], user_id)
    ).fetchone()
    return member is not None
