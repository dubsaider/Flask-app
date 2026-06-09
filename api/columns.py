from flask import jsonify, request
from .init import api_bp
from database import get_db_context
from models import Column, Card, User
from . import permissions as perm


def _forbidden(message):
    return jsonify({'error': message}), 403


@api_bp.route('/boards/<int:board_id>/columns', methods=['GET', 'POST'])
def columns_handler(board_id):
    if request.method == 'POST':
        data = request.json
        user_id = data.get('user_id')
        if not user_id:
            return _forbidden('user_id is required')

        with get_db_context() as conn:
            board = conn.execute('SELECT * FROM boards WHERE id = ?', (board_id,)).fetchone()
            if not board:
                return jsonify({'error': 'Board not found'}), 404

            role, error = perm.check_access(conn, board['team_id'], user_id)
            if error:
                return jsonify({'error': error[0]}), error[1]

            if not perm.can_manage_columns(role):
                return _forbidden('Only team leader can manage columns')

            max_pos = conn.execute(
                'SELECT COALESCE(MAX(position), -1) as max_pos FROM columns WHERE board_id = ?',
                (board_id,)
            ).fetchone()['max_pos']

            cursor = conn.execute(
                'INSERT INTO columns (title, position, board_id, is_done) VALUES (?, ?, ?, ?)',
                (data['title'], max_pos + 1, board_id, 1 if data.get('is_done') else 0)
            )
            column = conn.execute('SELECT * FROM columns WHERE id = ?', (cursor.lastrowid,)).fetchone()
            return jsonify(Column(column).to_dict()), 201

    with get_db_context() as conn:
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


@api_bp.route('/boards/<int:board_id>/columns/reorder', methods=['PUT'])
def reorder_columns(board_id):
    data = request.json
    user_id = data.get('user_id')
    column_ids = data.get('column_ids', [])

    if not user_id:
        return _forbidden('user_id is required')

    with get_db_context() as conn:
        board = conn.execute('SELECT * FROM boards WHERE id = ?', (board_id,)).fetchone()
        if not board:
            return jsonify({'error': 'Board not found'}), 404

        role, error = perm.check_access(conn, board['team_id'], user_id)
        if error:
            return jsonify({'error': error[0]}), error[1]

        if not perm.can_manage_columns(role):
            return _forbidden('Only team leader can manage columns')

        existing = conn.execute(
            'SELECT id FROM columns WHERE board_id = ? ORDER BY position',
            (board_id,)
        ).fetchall()
        existing_ids = {row['id'] for row in existing}

        if set(column_ids) != existing_ids:
            return jsonify({'error': 'Invalid column order'}), 400

        for position, column_id in enumerate(column_ids):
            conn.execute(
                'UPDATE columns SET position = ? WHERE id = ? AND board_id = ?',
                (position, column_id, board_id)
            )

        return jsonify({'message': 'Columns reordered'})


@api_bp.route('/columns/<int:column_id>', methods=['PUT', 'DELETE'])
def column_handler(column_id):
    with get_db_context() as conn:
        team_id = perm.get_team_id_for_column(conn, column_id)
        if not team_id:
            return jsonify({'error': 'Column not found'}), 404

        if request.method == 'PUT':
            data = request.json
            user_id = data.get('user_id')
            if not user_id:
                return _forbidden('user_id is required')

            role, error = perm.check_access(conn, team_id, user_id)
            if error:
                return jsonify({'error': error[0]}), error[1]

            if not perm.can_manage_columns(role):
                return _forbidden('Only team leader can manage columns')

            conn.execute(
                'UPDATE columns SET title = ?, is_done = ? WHERE id = ?',
                (data['title'], 1 if data.get('is_done') else 0, column_id)
            )
            column = conn.execute('SELECT * FROM columns WHERE id = ?', (column_id,)).fetchone()
            if column:
                return jsonify(Column(column).to_dict())
            return jsonify({'error': 'Column not found'}), 404

        elif request.method == 'DELETE':
            data = request.json or {}
            user_id = data.get('user_id')
            if not user_id:
                return _forbidden('user_id is required')

            role, error = perm.check_access(conn, team_id, user_id)
            if error:
                return jsonify({'error': error[0]}), error[1]

            if not perm.can_manage_columns(role):
                return _forbidden('Only team leader can manage columns')

            conn.execute('DELETE FROM columns WHERE id = ?', (column_id,))
            return '', 204
