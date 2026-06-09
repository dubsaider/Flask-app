from flask import jsonify, request
from .init import api_bp
from database import get_db_context
from models import Board
from . import permissions as perm


def _forbidden(message):
    return jsonify({'error': message}), 403


@api_bp.route('/boards', methods=['GET', 'POST'])
def boards_handler():
    if request.method == 'POST':
        data = request.json
        user_id = data.get('user_id')
        if not user_id:
            return _forbidden('user_id is required')

        with get_db_context() as conn:
            team = conn.execute('SELECT * FROM teams WHERE id = ?', (data['team_id'],)).fetchone()
            if not team:
                return jsonify({'error': 'Team not found'}), 404

            _, error = perm.check_access(conn, team['id'], user_id)
            if error:
                return jsonify({'error': error[0]}), error[1]

            if not perm.can_manage_board(conn, team['id'], user_id):
                return _forbidden('You cannot create boards')

            cursor = conn.execute(
                'INSERT INTO boards (title, description, team_id) VALUES (?, ?, ?)',
                (data['title'], data.get('description', ''), data['team_id'])
            )
            board_id = cursor.lastrowid

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
            user_id = data.get('user_id')
            if not user_id:
                return _forbidden('user_id is required')

            board = conn.execute('SELECT * FROM boards WHERE id = ?', (board_id,)).fetchone()
            if not board:
                return jsonify({'error': 'Board not found'}), 404

            _, error = perm.check_access(conn, board['team_id'], user_id)
            if error:
                return jsonify({'error': error[0]}), error[1]

            if not perm.can_manage_board(conn, board['team_id'], user_id):
                return _forbidden('You cannot edit boards')

            conn.execute(
                'UPDATE boards SET title = ?, description = ? WHERE id = ?',
                (data['title'], data.get('description', ''), board_id)
            )
            board = conn.execute('SELECT * FROM boards WHERE id = ?', (board_id,)).fetchone()
            return jsonify(Board(board).to_dict())

        elif request.method == 'DELETE':
            data = request.json or {}
            user_id = data.get('user_id')
            if not user_id:
                return _forbidden('user_id is required')

            board = conn.execute('SELECT * FROM boards WHERE id = ?', (board_id,)).fetchone()
            if not board:
                return jsonify({'error': 'Board not found'}), 404

            _, error = perm.check_access(conn, board['team_id'], user_id)
            if error:
                return jsonify({'error': error[0]}), error[1]

            if not perm.can_manage_board(conn, board['team_id'], user_id):
                return _forbidden('You cannot delete boards')

            conn.execute('DELETE FROM boards WHERE id = ?', (board_id,))
            return '', 204

        board = conn.execute('SELECT * FROM boards WHERE id = ?', (board_id,)).fetchone()
        if board:
            return jsonify(Board(board).to_dict())
        return jsonify({'error': 'Board not found'}), 404
