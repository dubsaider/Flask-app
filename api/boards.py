from flask import jsonify, request
from .init import api_bp
from .db import session_scope
from .http_helpers import forbidden, not_found, access_denied
from models import Board
from models.schema import Board as BoardModel, Column as ColumnModel, Team as TeamModel
from . import permissions as perm


@api_bp.route('/boards', methods=['GET', 'POST'])
def boards_handler():
    if request.method == 'POST':
        data = request.json
        user_id = data.get('user_id')
        if not user_id:
            return forbidden('user_id is required')

        with session_scope() as session:
            team = session.get(TeamModel, data['team_id'])
            if not team:
                return not_found('Team not found')

            _, error = perm.check_access(session, team.id, user_id)
            denied = access_denied(error)
            if denied:
                return denied

            if not perm.can_manage_board(session, team.id, user_id):
                return forbidden('You cannot create boards')

            board = BoardModel(
                title=data['title'],
                description=data.get('description', ''),
                team_id=data['team_id'],
            )
            session.add(board)
            session.flush()

            default_columns = ['To Do', 'In Progress', 'Done']
            for i, col_title in enumerate(default_columns):
                session.add(ColumnModel(title=col_title, position=i, board_id=board.id))

            return jsonify(Board(board).to_dict()), 201

    with session_scope() as session:
        boards = session.query(BoardModel).all()
        return jsonify([Board(board).to_dict() for board in boards])


@api_bp.route('/boards/<int:board_id>', methods=['GET', 'PUT', 'DELETE'])
def board_handler(board_id):
    with session_scope() as session:
        board = session.get(BoardModel, board_id)

        if request.method == 'PUT':
            data = request.json
            user_id = data.get('user_id')
            if not user_id:
                return forbidden('user_id is required')
            if not board:
                return not_found('Board not found')

            _, error = perm.check_access(session, board.team_id, user_id)
            denied = access_denied(error)
            if denied:
                return denied

            if not perm.can_manage_board(session, board.team_id, user_id):
                return forbidden('You cannot edit boards')

            board.title = data['title']
            board.description = data.get('description', '')
            return jsonify(Board(board).to_dict())

        if request.method == 'DELETE':
            data = request.json or {}
            user_id = data.get('user_id')
            if not user_id:
                return forbidden('user_id is required')
            if not board:
                return not_found('Board not found')

            _, error = perm.check_access(session, board.team_id, user_id)
            denied = access_denied(error)
            if denied:
                return denied

            if not perm.can_manage_board(session, board.team_id, user_id):
                return forbidden('You cannot delete boards')

            session.delete(board)
            return '', 204

        if board:
            return jsonify(Board(board).to_dict())
        return not_found('Board not found')
