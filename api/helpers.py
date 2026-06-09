from models import User, Team
from .role_helpers import load_team_roles, seed_default_roles


def load_team(conn, team_row):
    team_obj = Team(team_row)
    seed_default_roles(conn, team_obj.id)

    members = conn.execute('''
        SELECT u.*, tm.role_id,
               tr.slug AS role_slug, tr.name AS role_name
        FROM users u
        JOIN team_members tm ON u.id = tm.user_id
        JOIN team_roles tr ON tm.role_id = tr.id
        WHERE tm.team_id = ?
        ORDER BY u.username
    ''', (team_obj.id,)).fetchall()

    team_obj.members = []
    for member_row in members:
        user = User(member_row)
        user.role_id = member_row['role_id']
        user.role = member_row['role_slug']
        user.role_name = member_row['role_name']
        team_obj.members.append(user)

    if team_obj.curator_id:
        curator = conn.execute(
            'SELECT * FROM users WHERE id = ?',
            (team_obj.curator_id,)
        ).fetchone()
        if curator:
            team_obj.curator = User(curator)

    team_obj.roles = load_team_roles(conn, team_obj.id)
    return team_obj


def user_has_team_access(conn, team_row, user_id):
    from .permissions import can_view
    return can_view(conn, team_row['id'], user_id)
