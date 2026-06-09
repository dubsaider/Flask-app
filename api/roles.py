from flask import jsonify, request
from .init import api_bp
from database import get_db_context
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


def _forbidden(message):
    return jsonify({'error': message}), 403


@api_bp.route('/role-templates', methods=['GET'])
def get_role_templates():
    from .role_templates import templates_for_api
    return jsonify({
        'templates': templates_for_api(),
        'permission_labels': PERMISSION_LABELS,
    })


@api_bp.route('/teams/<int:team_id>/roles', methods=['GET', 'POST'])
def team_roles_handler(team_id):
    with get_db_context() as conn:
        team = conn.execute('SELECT * FROM teams WHERE id = ?', (team_id,)).fetchone()
        if not team:
            return jsonify({'error': 'Team not found'}), 404

        seed_default_roles(conn, team_id)

        if request.method == 'GET':
            user_id = request.args.get('user_id', type=int)
            if not user_id:
                return _forbidden('user_id is required')
            if not perm.can_view(conn, team_id, user_id):
                return _forbidden('Access denied')
            return jsonify(load_team_roles(conn, team_id))

        data = request.get_json(silent=True) or {}
        user_id = data.get('user_id')
        if not user_id:
            return _forbidden('user_id is required')
        if not perm.can_manage_roles(conn, team_id, user_id):
            return _forbidden('Only users with role management permission can create roles')

        template_key = data.get('template_key')
        if template_key and template_key in ROLE_TEMPLATES:
            template = ROLE_TEMPLATES[template_key]
            name = data.get('name') or f"{template['name']} (копия)"
            base_slug = data.get('slug') or template_key
            permissions = normalize_permissions(template['permissions'])
            if data.get('permissions'):
                permissions = normalize_permissions(data['permissions'])
            description = data.get('description') or template['description']
            is_system = 0
        else:
            name = (data.get('name') or '').strip()
            if not name:
                return jsonify({'error': 'Role name is required'}), 400
            base_slug = data.get('slug') or name.lower().replace(' ', '-')
            permissions = normalize_permissions(data.get('permissions'))
            description = data.get('description', '')
            is_system = 0

        slug = unique_slug(conn, team_id, base_slug)
        cursor = conn.execute(
            '''INSERT INTO team_roles
               (team_id, name, slug, description, permissions, is_system, template_key)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (
                team_id,
                name,
                slug,
                description,
                serialize_permissions(permissions),
                is_system,
                template_key,
            )
        )
        role = get_team_role_by_id(conn, team_id, cursor.lastrowid)
        return jsonify(role_row_to_dict(role)), 201


@api_bp.route('/teams/<int:team_id>/roles/<int:role_id>', methods=['PUT', 'DELETE'])
def team_role_handler(team_id, role_id):
    data = request.get_json(silent=True) or {}
    user_id = data.get('user_id')

    with get_db_context() as conn:
        role = get_team_role_by_id(conn, team_id, role_id)
        if not role:
            return jsonify({'error': 'Role not found'}), 404

        if not user_id:
            return _forbidden('user_id is required')
        if not perm.can_manage_roles(conn, team_id, user_id):
            return _forbidden('Only users with role management permission can modify roles')

        if request.method == 'DELETE':
            if role['is_system']:
                return jsonify({'error': 'System roles cannot be deleted'}), 400
            members_count = count_members_with_role(conn, role_id)
            if members_count:
                return jsonify({'error': 'Role is assigned to team members'}), 400
            conn.execute('DELETE FROM team_roles WHERE id = ? AND team_id = ?', (role_id, team_id))
            return '', 204

        if role['template_key'] == 'leader' and data.get('permissions'):
            leader_perms = normalize_permissions(data['permissions'])
            if not leader_perms.get('manage_roles'):
                return jsonify({'error': 'Leader role must keep role management permission'}), 400

        name = data.get('name', role['name']).strip()
        description = data.get('description', role['description'])
        permissions = normalize_permissions(data.get('permissions', role['permissions']))

        conn.execute(
            '''UPDATE team_roles
               SET name = ?, description = ?, permissions = ?
               WHERE id = ? AND team_id = ?''',
            (name, description, serialize_permissions(permissions), role_id, team_id)
        )
        updated = get_team_role_by_id(conn, team_id, role_id)
        return jsonify(role_row_to_dict(updated))
