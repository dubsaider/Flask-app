from flask import jsonify, request
from .init import api_bp
from .db import session_scope
from .http_helpers import forbidden, not_found, bad_request
from . import permissions as perm
from .role_templates import PERMISSION_LABELS, ROLE_TEMPLATES, normalize_permissions, serialize_permissions
from .role_helpers import (
    load_team_roles,
    get_team_role_by_id,
    role_row_to_dict,
    unique_slug,
    count_members_with_role,
    seed_default_roles,
)
from models.schema import Team as TeamModel, TeamRole


@api_bp.route('/role-templates', methods=['GET'])
def get_role_templates():
    from .role_templates import templates_for_api
    return jsonify({
        'templates': templates_for_api(),
        'permission_labels': PERMISSION_LABELS,
    })


@api_bp.route('/teams/<int:team_id>/roles', methods=['GET', 'POST'])
def team_roles_handler(team_id):
    with session_scope() as session:
        team = session.get(TeamModel, team_id)
        if not team:
            return not_found('Team not found')

        seed_default_roles(session, team_id)

        if request.method == 'GET':
            user_id = request.args.get('user_id', type=int)
            if not user_id:
                return forbidden('user_id is required')
            if not perm.can_view(session, team_id, user_id):
                return forbidden('Access denied')
            return jsonify(load_team_roles(session, team_id))

        data = request.get_json(silent=True) or {}
        user_id = data.get('user_id')
        if not user_id:
            return forbidden('user_id is required')
        if not perm.can_manage_roles(session, team_id, user_id):
            return forbidden('Only users with role management permission can create roles')

        template_key = data.get('template_key')
        if template_key and template_key in ROLE_TEMPLATES:
            template = ROLE_TEMPLATES[template_key]
            name = data.get('name') or f"{template['name']} (копия)"
            base_slug = data.get('slug') or template_key
            permissions = normalize_permissions(template['permissions'])
            if data.get('permissions'):
                permissions = normalize_permissions(data['permissions'])
            description = data.get('description') or template['description']
            is_system = False
        else:
            name = (data.get('name') or '').strip()
            if not name:
                return bad_request('Role name is required')
            base_slug = data.get('slug') or name.lower().replace(' ', '-')
            permissions = normalize_permissions(data.get('permissions'))
            description = data.get('description', '')
            is_system = False

        slug = unique_slug(session, team_id, base_slug)
        role = TeamRole(
            team_id=team_id,
            name=name,
            slug=slug,
            description=description,
            permissions=serialize_permissions(permissions),
            is_system=is_system,
            template_key=template_key,
        )
        session.add(role)
        session.flush()
        return jsonify(role_row_to_dict(role)), 201


@api_bp.route('/teams/<int:team_id>/roles/<int:role_id>', methods=['PUT', 'DELETE'])
def team_role_handler(team_id, role_id):
    data = request.get_json(silent=True) or {}
    user_id = data.get('user_id')

    with session_scope() as session:
        role = get_team_role_by_id(session, team_id, role_id)
        if not role:
            return not_found('Role not found')

        if not user_id:
            return forbidden('user_id is required')
        if not perm.can_manage_roles(session, team_id, user_id):
            return forbidden('Only users with role management permission can modify roles')

        if request.method == 'DELETE':
            if role.is_system:
                return bad_request('System roles cannot be deleted')
            members_count = count_members_with_role(session, role_id)
            if members_count:
                return bad_request('Role is assigned to team members')
            session.delete(role)
            return '', 204

        if role.template_key == 'leader' and data.get('permissions'):
            leader_perms = normalize_permissions(data['permissions'])
            if not leader_perms.get('manage_roles'):
                return bad_request('Leader role must keep role management permission')

        role.name = data.get('name', role.name).strip()
        role.description = data.get('description', role.description)
        role.permissions = serialize_permissions(data.get('permissions', role.permissions))
        return jsonify(role_row_to_dict(role))
