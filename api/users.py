from flask import jsonify, request
from .init import api_bp
from database import get_db_context
from models import User, Board
from .helpers import load_team, user_has_team_access
from . import permissions as perm

@api_bp.route('/users', methods=['GET'])
def get_users():
    with get_db_context() as conn:
        users = conn.execute('SELECT * FROM users').fetchall()
        return jsonify([User(user).to_dict() for user in users])

@api_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    with get_db_context() as conn:
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        if user:
            return jsonify(User(user).to_dict())
        return jsonify({'error': 'User not found'}), 404

@api_bp.route('/users/<int:user_id>/workspace', methods=['GET'])
def get_user_workspace(user_id):
    """Доски пользователя, сгруппированные по командам"""
    with get_db_context() as conn:
        teams = conn.execute('SELECT * FROM teams ORDER BY name').fetchall()
        workspace = []

        for team_row in teams:
            if not user_has_team_access(conn, team_row, user_id):
                continue

            boards = conn.execute(
                'SELECT * FROM boards WHERE team_id = ? ORDER BY title',
                (team_row['id'],)
            ).fetchall()

            role_info = perm.get_user_role_info(conn, team_row['id'], user_id)

            workspace.append({
                'team': {
                    'id': team_row['id'],
                    'name': team_row['name'],
                    'description': team_row['description'],
                    'curator_id': team_row['curator_id'],
                },
                'role': role_info['slug'],
                'role_name': role_info['name'],
                'role_id': role_info['role_id'],
                'permissions': role_info['permissions'],
                'boards': [Board(board).to_dict() for board in boards]
            })

        return jsonify(workspace)