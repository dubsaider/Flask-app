from flask import jsonify, request
from .init import api_bp
from database import get_db_context
from models import Column, Card, User

@api_bp.route('/boards/<int:board_id>/columns', methods=['GET', 'POST'])
def columns_handler(board_id):
    if request.method == 'POST':
        data = request.json
        with get_db_context() as conn:
            # Проверяем, существует ли доска
            board = conn.execute('SELECT * FROM boards WHERE id = ?', (board_id,)).fetchone()
            if not board:
                return jsonify({'error': 'Board not found'}), 404
                
            max_pos = conn.execute(
                'SELECT COALESCE(MAX(position), -1) as max_pos FROM columns WHERE board_id = ?',
                (board_id,)
            ).fetchone()['max_pos']
            
            cursor = conn.execute(
                'INSERT INTO columns (title, position, board_id) VALUES (?, ?, ?)',
                (data['title'], max_pos + 1, board_id)
            )
            column = conn.execute('SELECT * FROM columns WHERE id = ?', (cursor.lastrowid,)).fetchone()
            return jsonify(Column(column).to_dict()), 201
    
    # GET запрос
    with get_db_context() as conn:
        # Проверяем, существует ли доска
        board = conn.execute('SELECT * FROM boards WHERE id = ?', (board_id,)).fetchone()
        if not board:
            return jsonify({'error': 'Board not found'}), 404
            
        columns = conn.execute(
            'SELECT * FROM columns WHERE board_id = ? ORDER BY position',
            (board_id,)
        ).fetchall()
        
        result = []
        for col in columns:
            column = Column(col)
            cards = conn.execute(
                'SELECT * FROM cards WHERE column_id = ? ORDER BY position',
                (column.id,)
            ).fetchall()
            column.cards = []
            for card_row in cards:
                card = Card(card_row)
                if card.assignee_id:
                    assignee = conn.execute(
                        'SELECT * FROM users WHERE id = ?',
                        (card.assignee_id,)
                    ).fetchone()
                    if assignee:
                        card.assignee = User(assignee)
                column.cards.append(card)
            result.append(column.to_dict())
        
        return jsonify(result)

@api_bp.route('/columns/<int:column_id>', methods=['PUT', 'DELETE'])
def column_handler(column_id):
    with get_db_context() as conn:
        if request.method == 'PUT':
            data = request.json
            conn.execute(
                'UPDATE columns SET title = ? WHERE id = ?',
                (data['title'], column_id)
            )
            column = conn.execute('SELECT * FROM columns WHERE id = ?', (column_id,)).fetchone()
            if column:
                return jsonify(Column(column).to_dict())
            return jsonify({'error': 'Column not found'}), 404
            
        elif request.method == 'DELETE':
            conn.execute('DELETE FROM columns WHERE id = ?', (column_id,))
            return '', 204