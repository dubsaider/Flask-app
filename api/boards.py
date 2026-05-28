from flask import jsonify, request
from .init import api_bp
from database import get_db_context
from models import Board

@api_bp.route('/boards', methods=['GET', 'POST'])
def boards_handler():
    if request.method == 'POST':
        data = request.json
        with get_db_context() as conn:
            # Проверяем, существует ли команда
            team = conn.execute('SELECT * FROM teams WHERE id = ?', (data['team_id'],)).fetchone()
            if not team:
                return jsonify({'error': 'Team not found'}), 404
                
            cursor = conn.execute(
                'INSERT INTO boards (title, description, team_id) VALUES (?, ?, ?)',
                (data['title'], data.get('description', ''), data['team_id'])
            )
            board_id = cursor.lastrowid
            
            # Создаем колонки по умолчанию
            default_columns = ['To Do', 'In Progress', 'Done']
            for i, col_title in enumerate(default_columns):
                conn.execute(
                    'INSERT INTO columns (title, position, board_id) VALUES (?, ?, ?)',
                    (col_title, i, board_id)
                )
            
            board = conn.execute('SELECT * FROM boards WHERE id = ?', (board_id,)).fetchone()
            return jsonify(Board(board).to_dict()), 201
    
    with get_db_context() as conn:
        boards = conn.execute('SELECT * FROM boards').fetchall()
        return jsonify([Board(board).to_dict() for board in boards])

@api_bp.route('/boards/<int:board_id>', methods=['GET', 'PUT', 'DELETE'])
def board_handler(board_id):
    with get_db_context() as conn:
        if request.method == 'PUT':
            data = request.json
            conn.execute(
                'UPDATE boards SET title = ?, description = ? WHERE id = ?',
                (data['title'], data.get('description', ''), board_id)
            )
            board = conn.execute('SELECT * FROM boards WHERE id = ?', (board_id,)).fetchone()
            if board:
                return jsonify(Board(board).to_dict())
            return jsonify({'error': 'Board not found'}), 404
            
        elif request.method == 'DELETE':
            conn.execute('DELETE FROM boards WHERE id = ?', (board_id,))
            return '', 204
        
        board = conn.execute('SELECT * FROM boards WHERE id = ?', (board_id,)).fetchone()
        if board:
            return jsonify(Board(board).to_dict())
        return jsonify({'error': 'Board not found'}), 404