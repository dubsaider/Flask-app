from flask import jsonify, request
from .init import api_bp
from database import get_db_context
from models import User, Team, Board
from .helpers import load_team
from . import permissions as perm
from .role_helpers import seed_default_roles, get_team_role_by_id


def _forbidden(message):
    return jsonify({'error': message}), 403


@api_bp.route('/teams', methods=['GET', 'POST'])
def teams_handler():
    if request.method == 'POST':
        data = request.json
        user_id = data.get('user_id')
        with get_db_context() as conn:
            cursor = conn.execute(
                'INSERT INTO teams (name, description) VALUES (?, ?)',
                (data['name'], data.get('description', ''))
            )
            team_id = cursor.lastrowid
            seed_default_roles(conn, team_id)

            if user_id:
                leader_role = conn.execute(
                    'SELECT id FROM team_roles WHERE team_id = ? AND template_key = ?',
                    (team_id, 'leader')
                ).fetchone()
                if leader_role:
                    conn.execute(
                        'INSERT OR IGNORE INTO team_members (team_id, user_id, role_id) VALUES (?, ?, ?)',
                        (team_id, user_id, leader_role['id'])
                    )

            team = conn.execute('SELECT * FROM teams WHERE id = ?', (team_id,)).fetchone()
            return jsonify(load_team(conn, team).to_dict()), 201

    with get_db_context() as conn:
        teams = conn.execute('SELECT * FROM teams').fetchall()
        result = []
        for team_row in teams:
            result.append(load_team(conn, team_row).to_dict())
        return jsonify(result)


@api_bp.route('/teams/<int:team_id>', methods=['GET', 'PUT', 'DELETE'])
def team_handler(team_id):
    with get_db_context() as conn:
        if request.method == 'PUT':
            data = request.json
            user_id = data.get('user_id')
            if not user_id:
                return _forbidden('user_id is required')
            if not perm.can_manage_team_members(conn, team_id, user_id):
                return _forbidden('You cannot edit team settings')

            conn.execute(
                'UPDATE teams SET name = ?, description = ? WHERE id = ?',
                (data['name'], data.get('description', ''), team_id)
            )
            if 'curator_id' in data:
                conn.execute(
                    'UPDATE teams SET curator_id = ? WHERE id = ?',
                    (data['curator_id'], team_id)
                )
            team = conn.execute('SELECT * FROM teams WHERE id = ?', (team_id,)).fetchone()
            if team:
                return jsonify(load_team(conn, team).to_dict())
            return jsonify({'error': 'Team not found'}), 404

        elif request.method == 'DELETE':
            data = request.json or {}
            user_id = data.get('user_id')
            if not user_id:
                return _forbidden('user_id is required')
            if not perm.can_manage_board(conn, team_id, user_id):
                return _forbidden('You cannot delete team')
            conn.execute('DELETE FROM teams WHERE id = ?', (team_id,))
            return '', 204

        team = conn.execute('SELECT * FROM teams WHERE id = ?', (team_id,)).fetchone()
        if team:
            return jsonify(load_team(conn, team).to_dict())
        return jsonify({'error': 'Team not found'}), 404


@api_bp.route('/teams/<int:team_id>/members', methods=['POST', 'DELETE'])
def team_members_handler(team_id):
    data = request.json or {}
    user_id = data.get('user_id')
    if not user_id:
        return _forbidden('user_id is required')

    if request.method == 'POST':
        with get_db_context() as conn:
            if not perm.can_manage_team_members(conn, team_id, user_id):
                return _forbidden('You cannot add team members')

            seed_default_roles(conn, team_id)
            role_id = data.get('role_id')
            if not role_id and data.get('role'):
                role_row = conn.execute(
                    'SELECT id FROM team_roles WHERE team_id = ? AND slug = ?',
                    (team_id, data['role'])
                ).fetchone()
                role_id = role_row['id'] if role_row else None
            if not role_id:
                default_role = conn.execute(
                    'SELECT id FROM team_roles WHERE team_id = ? AND template_key = ?',
                    (team_id, 'developer')
                ).fetchone()
                role_id = default_role['id'] if default_role else None
            if not role_id:
                return jsonify({'error': 'Role not found'}), 400

            role = get_team_role_by_id(conn, team_id, role_id)
            if not role:
                return jsonify({'error': 'Role not found'}), 400

            member_user_id = data.get('member_user_id') or data.get('new_user_id')
            if not member_user_id:
                return jsonify({'error': 'member_user_id is required'}), 400

            try:
                conn.execute(
                    'INSERT INTO team_members (team_id, user_id, role_id) VALUES (?, ?, ?)',
                    (team_id, member_user_id, role_id)
                )
                return jsonify({'message': 'Member added'}), 201
            except Exception:
                return jsonify({'error': 'User already in team or not found'}), 400

    with get_db_context() as conn:
        if not perm.can_manage_team_members(conn, team_id, user_id):
            return _forbidden('You cannot remove team members')

        member_user_id = data.get('member_user_id')
        if not member_user_id:
            return jsonify({'error': 'member_user_id is required'}), 400

        conn.execute(
            'DELETE FROM team_members WHERE team_id = ? AND user_id = ?',
            (team_id, member_user_id)
        )
        return '', 204


@api_bp.route('/teams/<int:team_id>/members/<int:member_user_id>', methods=['PUT'])
def update_team_member(team_id, member_user_id):
    data = request.json or {}
    user_id = data.get('user_id')
    role_id = data.get('role_id')

    if not user_id:
        return _forbidden('user_id is required')
    if not role_id:
        return jsonify({'error': 'role_id is required'}), 400

    with get_db_context() as conn:
        if not perm.can_manage_team_members(conn, team_id, user_id):
            return _forbidden('You cannot change member roles')

        role = get_team_role_by_id(conn, team_id, role_id)
        if not role:
            return jsonify({'error': 'Role not found'}), 400

        member = conn.execute(
            'SELECT 1 FROM team_members WHERE team_id = ? AND user_id = ?',
            (team_id, member_user_id)
        ).fetchone()
        if not member:
            return jsonify({'error': 'Member not found'}), 404

        conn.execute(
            'UPDATE team_members SET role_id = ? WHERE team_id = ? AND user_id = ?',
            (role_id, team_id, member_user_id)
        )
        return jsonify({'message': 'Member updated'})


@api_bp.route('/teams/<int:team_id>/boards', methods=['GET'])
def get_team_boards(team_id):
    with get_db_context() as conn:
        boards = conn.execute('SELECT * FROM boards WHERE team_id = ?', (team_id,)).fetchall()
        return jsonify([Board(board).to_dict() for board in boards])
