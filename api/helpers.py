from models import User, Team
from models.schema import User as UserModel
from models.schema import TeamMember, TeamRole
from .role_helpers import load_team_roles, seed_default_roles


def load_team(session, team):
    team_obj = Team(team)
    seed_default_roles(session, team_obj.id)

    members = (
        session.query(UserModel, TeamMember.role_id, TeamRole.slug, TeamRole.name)
        .join(TeamMember, UserModel.id == TeamMember.user_id)
        .join(TeamRole, TeamMember.role_id == TeamRole.id)
        .filter(TeamMember.team_id == team_obj.id)
        .order_by(UserModel.username)
        .all()
    )

    team_obj.members = []
    for user_model, role_id, role_slug, role_name in members:
        user = User(user_model)
        user.role_id = role_id
        user.role = role_slug
        user.role_name = role_name
        team_obj.members.append(user)

    if team_obj.curator_id:
        curator = session.get(UserModel, team_obj.curator_id)
        if curator:
            team_obj.curator = User(curator)

    team_obj.roles = load_team_roles(session, team_obj.id)
    return team_obj


def user_has_team_access(session, team, user_id):
    from .permissions import can_view
    team_id = team.id if hasattr(team, 'id') else team['id']
    return can_view(session, team_id, user_id)
