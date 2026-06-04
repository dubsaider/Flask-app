from flask import jsonify, request
from .init import api_bp
from database import get_db_context
from models import Comment, User

@api_bp.route('/cards/<int:card_id>/comments', methods=['GET', 'POST'])
def comments_handler(card_id):
    if request.method == 'POST':
        data = request.json
        with get_db_context() as conn:
            # Проверяем существование карточки
            card = conn.execute('SELECT * FROM cards WHERE id = ?', (card_id,)).fetchone()
            if not card:
                return jsonify({'error': 'Card not found'}), 404
            
            cursor = conn.execute(
                'INSERT INTO comments (text, card_id, user_id) VALUES (?, ?, ?)',
                (data['text'], card_id, data['user_id'])
            )
            comment = conn.execute('SELECT * FROM comments WHERE id = ?', (cursor.lastrowid,)).fetchone()
            return jsonify(Comment(comment).to_dict()), 201
    
    # GET запрос
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

@api_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
def comment_handler(comment_id):
    with get_db_context() as conn:
        conn.execute('DELETE FROM comments WHERE id = ?', (comment_id,))
        return '', 204