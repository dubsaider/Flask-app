from flask import jsonify, request
from .init import api_bp
from .db import session_scope
from models import User, Board
from models.schema import User as UserModel
from .helpers import load_team, user_has_team_access
from . import permissions as perm

@api_bp.route('/users', methods=['GET'])
def get_users():
    with session_scope() as session:
        users = session.query(UserModel).all()
        return jsonify([User(user).to_dict() for user in users])

@api_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    with session_scope() as session:
        user = session.get(UserModel, user_id)
        if user:
            return jsonify(User(user).to_dict())
        return jsonify({'error': 'User not found'}), 404

@api_bp.route('/users/<int:user_id>/workspace', methods=['GET'])
def get_user_workspace(user_id):
    """Доски пользователя, сгруппированные по командам"""
    from models.schema import Team as TeamModel, Board as BoardModel

    with session_scope() as session:
        teams = session.query(TeamModel).order_by(TeamModel.name).all()
        workspace = []

        for team in teams:
            if not user_has_team_access(session, team, user_id):
                continue

            boards = (
                session.query(BoardModel)
                .filter_by(team_id=team.id)
                .order_by(BoardModel.title)
                .all()
            )

            role_info = perm.get_user_role_info(session, team.id, user_id)

            workspace.append({
                'team': {
                    'id': team.id,
                    'name': team.name,
                    'description': team.description,
                    'curator_id': team.curator_id,
                },
                'role': role_info['slug'],
                'role_name': role_info['name'],
                'role_id': role_info['role_id'],
                'permissions': role_info['permissions'],
                'boards': [Board(board).to_dict() for board in boards]
            })

        return jsonify(workspace)
