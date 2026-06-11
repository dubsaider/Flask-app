from flask import jsonify, request
from .init import api_bp
from .db import session_scope
from .http_helpers import forbidden, not_found, access_denied
from models import Comment, User
from models.schema import Comment as CommentModel, User as UserModel
from . import permissions as perm
from utils.html_sanitize import sanitize_html
from .notify_helpers import notify_comment


@api_bp.route('/cards/<int:card_id>/comments', methods=['GET', 'POST'])
def comments_handler(card_id):
    if request.method == 'POST':
        data = request.json
        user_id = data.get('user_id')
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

            if not perm.can_comment(session, team_id, user_id):
                return forbidden('You cannot comment on this card')

            comment = CommentModel(
                text=sanitize_html(data['text']),
                card_id=card_id,
                user_id=user_id,
            )
            session.add(comment)
            session.flush()
            notify_comment(session, card_id, user_id)
            return jsonify(Comment(comment).to_dict()), 201

    with session_scope() as session:
        comments = (
            session.query(CommentModel)
            .filter_by(card_id=card_id)
            .order_by(CommentModel.created_at)
            .all()
        )

        result = []
        for comment_model in comments:
            comment = Comment(comment_model)
            author = session.get(UserModel, comment.user_id)
            if author:
                comment.author = User(author)
            result.append(comment.to_dict())

        return jsonify(result)
