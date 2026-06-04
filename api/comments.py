from flask import jsonify, request
from .init import api_bp
from database import get_db_context
from models import Comment, User
from . import permissions as perm


def _forbidden(message):
    return jsonify({'error': message}), 403


@api_bp.route('/cards/<int:card_id>/comments', methods=['GET', 'POST'])
def comments_handler(card_id):
    if request.method == 'POST':
        data = request.json
        user_id = data.get('user_id')
        if not user_id:
            return _forbidden('user_id is required')

        with get_db_context() as conn:
            card = perm.get_card(conn, card_id)
            if not card:
                return jsonify({'error': 'Card not found'}), 404

            team_id = perm.get_team_id_for_card(conn, card_id)
            role, error = perm.check_access(conn, team_id, user_id)
            if error:
                return jsonify({'error': error[0]}), error[1]

            if not perm.can_comment(role):
                return _forbidden('You cannot comment on this card')

            cursor = conn.execute(
                'INSERT INTO comments (text, card_id, user_id) VALUES (?, ?, ?)',
                (data['text'], card_id, user_id)
            )
            comment = conn.execute('SELECT * FROM comments WHERE id = ?', (cursor.lastrowid,)).fetchone()
            return jsonify(Comment(comment).to_dict()), 201

    with get_db_context() as conn:
        comments = conn.execute(
            'SELECT * FROM comments WHERE card_id = ? ORDER BY created_at',
            (card_id,)
        ).fetchall()

        result = []
        for comment_row in comments:
            comment = Comment(comment_row)
            author = conn.execute(
                'SELECT * FROM users WHERE id = ?',
                (comment.user_id,)
            ).fetchone()
            if author:
                comment.author = User(author)
            result.append(comment.to_dict())

        return jsonify(result)
