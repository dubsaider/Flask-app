"""Создание и загрузка ролей команды (SQLAlchemy)."""
from sqlalchemy import func

from models.schema import TeamRole, TeamMember
from models.seed import seed_default_roles_for_team
from .role_templates import normalize_permissions, serialize_permissions


def seed_default_roles(session, team_id):
    """Создать встроенные роли команды из шаблонов."""
    seed_default_roles_for_team(session, team_id)


def get_team_role_by_slug(session, team_id, slug):
    return session.query(TeamRole).filter_by(team_id=team_id, slug=slug).first()


def get_team_role_by_id(session, team_id, role_id):
    return session.query(TeamRole).filter_by(team_id=team_id, id=role_id).first()


def load_team_roles(session, team_id):
    rows = (
        session.query(TeamRole)
        .filter_by(team_id=team_id)
        .order_by(TeamRole.is_system.desc(), TeamRole.name)
        .all()
    )
    return [role_to_dict(row) for row in rows]


def role_to_dict(role):
    return {
        'id': role.id,
        'team_id': role.team_id,
        'name': role.name,
        'slug': role.slug,
        'description': role.description,
        'permissions': normalize_permissions(role.permissions),
        'is_system': bool(role.is_system),
        'template_key': role.template_key,
    }


role_row_to_dict = role_to_dict


def unique_slug(session, team_id, base_slug):
    slug = base_slug
    index = 2
    while session.query(TeamRole.id).filter_by(team_id=team_id, slug=slug).first():
        slug = f'{base_slug}-{index}'
        index += 1
    return slug


def count_members_with_role(session, role_id):
    return session.query(func.count(TeamMember.user_id)).filter_by(role_id=role_id).scalar() or 0
