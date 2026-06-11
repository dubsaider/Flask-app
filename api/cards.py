from flask import jsonify, request
from datetime import datetime
from sqlalchemy import func
from .init import api_bp
from .db import session_scope
from .http_helpers import forbidden, not_found, bad_request, access_denied
from models import Card, User, Comment
from models.schema import (
    Card as CardModel,
    Column as ColumnModel,
    Board as BoardModel,
    Comment as CommentModel,
    User as UserModel,
)
from . import permissions as perm
from utils.html_sanitize import sanitize_html
from .notify_helpers import notify_assignee, notify_comment


@api_bp.route('/cards', methods=['POST'])
def create_card():
    data = request.json
    user_id = data.get('user_id')

    if not user_id:
        return forbidden('user_id is required')

    with session_scope() as session:
        team_id = perm.get_team_id_for_column(session, data['column_id'])
        if not team_id:
            return not_found('Column not found')

        _, error = perm.check_access(session, team_id, user_id)
        denied = access_denied(error)
        if denied:
            return denied

        if not perm.can_create_card(session, team_id, user_id):
            return forbidden('You cannot create tasks')

        max_pos = (
            session.query(func.coalesce(func.max(CardModel.position), -1))
            .filter_by(column_id=data['column_id'])
            .scalar()
        )

        card = CardModel(
            title=data['title'],
            description=sanitize_html(data.get('description', '')),
            position=max_pos + 1,
            column_id=data['column_id'],
            assignee_id=data.get('assignee_id'),
            created_by=user_id,
            priority=data.get('priority', 'medium'),
            deadline=data.get('deadline'),
        )
        session.add(card)
        session.flush()

        assignee_id = data.get('assignee_id')
        if assignee_id:
            notify_assignee(session, card.id, assignee_id, user_id, action='assigned')
        return jsonify(Card(card).to_dict()), 201


@api_bp.route('/cards/<int:card_id>', methods=['GET', 'PUT', 'DELETE'])
def card_handler(card_id):
    with session_scope() as session:
        if request.method == 'PUT':
            data = request.json
            user_id = data.get('user_id')
            if not user_id:
                return forbidden('user_id is required')

            existing = perm.get_card(session, card_id)
            if not existing:
                return not_found('Card not found')

            team_id = perm.get_team_id_for_card(session, card_id)
            _, error = perm.check_access(session, team_id, user_id)
            denied = access_denied(error)
            if denied:
                return denied

            if not perm.can_edit_card(session, team_id, user_id, existing):
                return forbidden('You cannot edit this card')

            if 'assignee_id' in data and not perm.can_assign(session, team_id, user_id):
                return forbidden('You cannot change assignee')

            assignee_id = data['assignee_id'] if 'assignee_id' in data else existing.assignee_id
            old_assignee_id = existing.assignee_id

            new_status = existing.status
            if 'archived' in data:
                if not perm.can_archive(session, team_id, user_id):
                    return forbidden('You cannot archive tasks')
                new_status = 'archived' if data['archived'] else 'active'
            elif 'status' in data:
                if data['status'] not in ('active', 'archived'):
                    return bad_request('Invalid status')
                if data['status'] == 'archived' and not perm.can_archive(session, team_id, user_id):
                    return forbidden('You cannot archive tasks')
                new_status = data['status']

            existing.title = data['title']
            existing.description = sanitize_html(data.get('description', ''))
            existing.assignee_id = assignee_id
            existing.priority = data.get('priority', 'medium')
            existing.status = new_status
            existing.deadline = data.get('deadline')
            existing.updated_at = datetime.utcnow()

            if assignee_id and assignee_id != old_assignee_id:
                notify_assignee(session, card_id, assignee_id, user_id, action='reassigned')

            column = session.get(ColumnModel, existing.column_id)
            column_is_done = bool(column.is_done) if column else False
            return jsonify(Card(existing).to_dict(column_is_done=column_is_done))

        if request.method == 'DELETE':
            data = request.json or {}
            user_id = data.get('user_id')
            if not user_id:
                return forbidden('user_id is required')

            team_id = perm.get_team_id_for_card(session, card_id)
            _, error = perm.check_access(session, team_id, user_id)
            denied = access_denied(error)
            if denied:
                return denied

            if not perm.can_delete_card(session, team_id, user_id):
                return forbidden('You cannot delete tasks')

            card = session.get(CardModel, card_id)
            if card:
                session.delete(card)
            return '', 204

        card_model = session.get(CardModel, card_id)
        if card_model:
            card_obj = Card(card_model)

            if card_obj.assignee_id:
                assignee = session.get(UserModel, card_obj.assignee_id)
                if assignee:
                    card_obj.assignee = User(assignee)

            if card_obj.created_by:
                creator = session.get(UserModel, card_obj.created_by)
                if creator:
                    card_obj.creator = User(creator)

            comments = (
                session.query(CommentModel)
                .filter_by(card_id=card_id)
                .order_by(CommentModel.created_at)
                .all()
            )

            for comment_model in comments:
                comment = Comment(comment_model)
                author = session.get(UserModel, comment.user_id)
                if author:
                    comment.author = User(author)
                card_obj.comments.append(comment)

            column = session.get(ColumnModel, card_obj.column_id)
            column_is_done = bool(column.is_done) if column else False

            return jsonify(card_obj.to_dict(column_is_done=column_is_done))
        return not_found('Card not found')


@api_bp.route('/cards/<int:card_id>/move', methods=['PUT'])
def move_card(card_id):
    data = request.json
    user_id = data.get('user_id')
    new_column_id = data['column_id']
    new_position = data['position']

    if not user_id:
        return forbidden('user_id is required')

    with session_scope() as session:
        card = perm.get_card(session, card_id)
        if not card:
            return not_found('Card not found')

        team_id = perm.get_team_id_for_card(session, card_id)
        _, error = perm.check_access(session, team_id, user_id)
        denied = access_denied(error)
        if denied:
            return denied

        if not perm.can_move_card(session, team_id, user_id, card):
            return forbidden('You cannot move this card')

        new_column = session.get(ColumnModel, new_column_id)
        if not new_column:
            return not_found('Target column not found')

        card_board = (
            session.query(BoardModel.id)
            .join(ColumnModel, ColumnModel.board_id == BoardModel.id)
            .filter(ColumnModel.id == card.column_id)
            .first()
        )
        if not card_board or new_column.board_id != card_board[0]:
            return forbidden('Cannot move card to another board')

        old_column_id = card.column_id
        old_position = card.position

        if old_column_id == new_column_id:
            if new_position > old_position:
                session.query(CardModel).filter(
                    CardModel.column_id == old_column_id,
                    CardModel.position > old_position,
                    CardModel.position <= new_position,
                    CardModel.id != card_id,
                ).update({CardModel.position: CardModel.position - 1}, synchronize_session=False)
            elif new_position < old_position:
                session.query(CardModel).filter(
                    CardModel.column_id == old_column_id,
                    CardModel.position >= new_position,
                    CardModel.position < old_position,
                    CardModel.id != card_id,
                ).update({CardModel.position: CardModel.position + 1}, synchronize_session=False)
            card.position = new_position
        else:
            session.query(CardModel).filter(
                CardModel.column_id == old_column_id,
                CardModel.position > old_position,
            ).update({CardModel.position: CardModel.position - 1}, synchronize_session=False)
            session.query(CardModel).filter(
                CardModel.column_id == new_column_id,
                CardModel.position >= new_position,
            ).update({CardModel.position: CardModel.position + 1}, synchronize_session=False)
            card.column_id = new_column_id
            card.position = new_position

        card.updated_at = datetime.utcnow()
        return jsonify({'message': 'Card moved successfully'})
