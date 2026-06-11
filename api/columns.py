from flask import jsonify, request
from sqlalchemy import func
from .init import api_bp
from .db import session_scope
from .http_helpers import forbidden, not_found, bad_request, access_denied
from models import Column, Card, User
from models.schema import (
    Board as BoardModel,
    Column as ColumnModel,
    Card as CardModel,
    User as UserModel,
)
from . import permissions as perm


@api_bp.route('/boards/<int:board_id>/columns', methods=['GET', 'POST'])
def columns_handler(board_id):
    if request.method == 'POST':
        data = request.json
        user_id = data.get('user_id')
        if not user_id:
            return forbidden('user_id is required')

        with session_scope() as session:
            board = session.get(BoardModel, board_id)
            if not board:
                return not_found('Board not found')

            _, error = perm.check_access(session, board.team_id, user_id)
            denied = access_denied(error)
            if denied:
                return denied

            if not perm.can_manage_columns(session, board.team_id, user_id):
                return forbidden('You cannot manage columns')

            max_pos = (
                session.query(func.coalesce(func.max(ColumnModel.position), -1))
                .filter_by(board_id=board_id)
                .scalar()
            )

            column = ColumnModel(
                title=data['title'],
                position=max_pos + 1,
                board_id=board_id,
                is_done=bool(data.get('is_done')),
            )
            session.add(column)
            session.flush()
            return jsonify(Column(column).to_dict()), 201

    with session_scope() as session:
        board = session.get(BoardModel, board_id)
        if not board:
            return not_found('Board not found')

        columns = (
            session.query(ColumnModel)
            .filter_by(board_id=board_id)
            .order_by(ColumnModel.position)
            .all()
        )

        result = []
        for col in columns:
            column = Column(col)
            cards = (
                session.query(CardModel)
                .filter_by(column_id=column.id)
                .order_by(CardModel.position)
                .all()
            )
            column.cards = []
            for card_model in cards:
                card = Card(card_model)
                if card.assignee_id:
                    assignee = session.get(UserModel, card.assignee_id)
                    if assignee:
                        card.assignee = User(assignee)
                column.cards.append(card)
            result.append(column.to_dict())

        return jsonify(result)


@api_bp.route('/boards/<int:board_id>/columns/reorder', methods=['PUT'])
def reorder_columns(board_id):
    data = request.json
    user_id = data.get('user_id')
    column_ids = data.get('column_ids', [])

    if not user_id:
        return forbidden('user_id is required')

    with session_scope() as session:
        board = session.get(BoardModel, board_id)
        if not board:
            return not_found('Board not found')

        _, error = perm.check_access(session, board.team_id, user_id)
        denied = access_denied(error)
        if denied:
            return denied

        if not perm.can_manage_columns(session, board.team_id, user_id):
            return forbidden('You cannot manage columns')

        existing = (
            session.query(ColumnModel.id)
            .filter_by(board_id=board_id)
            .order_by(ColumnModel.position)
            .all()
        )
        existing_ids = {row[0] for row in existing}

        if set(column_ids) != existing_ids:
            return bad_request('Invalid column order')

        for position, column_id in enumerate(column_ids):
            column = session.get(ColumnModel, column_id)
            if column and column.board_id == board_id:
                column.position = position

        return jsonify({'message': 'Columns reordered'})


@api_bp.route('/columns/<int:column_id>', methods=['PUT', 'DELETE'])
def column_handler(column_id):
    with session_scope() as session:
        team_id = perm.get_team_id_for_column(session, column_id)
        if not team_id:
            return not_found('Column not found')

        if request.method == 'PUT':
            data = request.json
            user_id = data.get('user_id')
            if not user_id:
                return forbidden('user_id is required')

            _, error = perm.check_access(session, team_id, user_id)
            denied = access_denied(error)
            if denied:
                return denied

            if not perm.can_manage_columns(session, team_id, user_id):
                return forbidden('You cannot manage columns')

            column = session.get(ColumnModel, column_id)
            if not column:
                return not_found('Column not found')

            column.title = data['title']
            column.is_done = bool(data.get('is_done'))
            return jsonify(Column(column).to_dict())

        data = request.json or {}
        user_id = data.get('user_id')
        if not user_id:
            return forbidden('user_id is required')

        _, error = perm.check_access(session, team_id, user_id)
        denied = access_denied(error)
        if denied:
            return denied

        if not perm.can_manage_columns(session, team_id, user_id):
            return forbidden('You cannot manage columns')

        column = session.get(ColumnModel, column_id)
        if column:
            session.delete(column)
        return '', 204
