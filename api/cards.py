from flask import jsonify, request
from datetime import datetime
from .init import api_bp
from database import get_db_context
from models import Card, User, Comment
from . import permissions as perm


def _forbidden(message):
    return jsonify({'error': message}), 403


@api_bp.route('/cards', methods=['POST'])
def create_card():
    data = request.json
    user_id = data.get('user_id')

    if not user_id:
        return _forbidden('user_id is required')

    with get_db_context() as conn:
        team_id = perm.get_team_id_for_column(conn, data['column_id'])
        if not team_id:
            return jsonify({'error': 'Column not found'}), 404

        role, error = perm.check_access(conn, team_id, user_id)
        if error:
            return jsonify({'error': error[0]}), error[1]

        if not perm.can_create_card(role):
            return _forbidden('Only team leader can create tasks')

        max_pos = conn.execute(
            'SELECT COALESCE(MAX(position), -1) as max_pos FROM cards WHERE column_id = ?',
            (data['column_id'],)
        ).fetchone()['max_pos']

        cursor = conn.execute(
            '''INSERT INTO cards (title, description, position, column_id, assignee_id, created_by, priority, deadline)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (data['title'], data.get('description', ''), max_pos + 1, data['column_id'],
             data.get('assignee_id'), user_id, data.get('priority', 'medium'),
             data.get('deadline'))
        )
        card = conn.execute('SELECT * FROM cards WHERE id = ?', (cursor.lastrowid,)).fetchone()
        return jsonify(Card(card).to_dict()), 201


@api_bp.route('/cards/<int:card_id>', methods=['GET', 'PUT', 'DELETE'])
def card_handler(card_id):
    with get_db_context() as conn:
        if request.method == 'PUT':
            data = request.json
            user_id = data.get('user_id')
            if not user_id:
                return _forbidden('user_id is required')

            existing = perm.get_card(conn, card_id)
            if not existing:
                return jsonify({'error': 'Card not found'}), 404

            team_id = perm.get_team_id_for_card(conn, card_id)
            role, error = perm.check_access(conn, team_id, user_id)
            if error:
                return jsonify({'error': error[0]}), error[1]

            if not perm.can_edit_card(role, existing, user_id):
                return _forbidden('You cannot edit this card')

            if 'assignee_id' in data and not perm.can_assign(role):
                return _forbidden('Only team leader can change assignee')

            assignee_id = data['assignee_id'] if 'assignee_id' in data else existing['assignee_id']

            new_status = existing['status']
            if 'archived' in data:
                if not perm.can_manage_board(role):
                    return _forbidden('Only team leader can archive tasks')
                new_status = 'archived' if data['archived'] else 'active'
            elif 'status' in data:
                if data['status'] not in ('active', 'archived'):
                    return jsonify({'error': 'Invalid status'}), 400
                if data['status'] == 'archived' and not perm.can_manage_board(role):
                    return _forbidden('Only team leader can archive tasks')
                new_status = data['status']

            conn.execute(
                '''UPDATE cards
                   SET title = ?, description = ?, assignee_id = ?, priority = ?,
                       status = ?, deadline = ?, updated_at = ?
                   WHERE id = ?''',
                (data['title'], data.get('description', ''), assignee_id,
                 data.get('priority', 'medium'), new_status,
                 data.get('deadline'), datetime.now(), card_id)
            )
            card = conn.execute('SELECT * FROM cards WHERE id = ?', (card_id,)).fetchone()
            column = conn.execute(
                'SELECT is_done FROM columns WHERE id = ?',
                (card['column_id'],)
            ).fetchone()
            return jsonify(Card(card).to_dict(column_is_done=bool(column['is_done'])))

        elif request.method == 'DELETE':
            data = request.json or {}
            user_id = data.get('user_id')
            if not user_id:
                return _forbidden('user_id is required')

            team_id = perm.get_team_id_for_card(conn, card_id)
            role, error = perm.check_access(conn, team_id, user_id)
            if error:
                return jsonify({'error': error[0]}), error[1]

            if not perm.can_delete_card(role):
                return _forbidden('Only team leader can delete tasks')

            conn.execute('DELETE FROM cards WHERE id = ?', (card_id,))
            return '', 204

        card = conn.execute('SELECT * FROM cards WHERE id = ?', (card_id,)).fetchone()
        if card:
            card_obj = Card(card)

            if card_obj.assignee_id:
                assignee = conn.execute('SELECT * FROM users WHERE id = ?', (card_obj.assignee_id,)).fetchone()
                if assignee:
                    card_obj.assignee = User(assignee)

            if card_obj.created_by:
                creator = conn.execute('SELECT * FROM users WHERE id = ?', (card_obj.created_by,)).fetchone()
                if creator:
                    card_obj.creator = User(creator)

            comments = conn.execute(
                'SELECT * FROM comments WHERE card_id = ? ORDER BY created_at',
                (card_id,)
            ).fetchall()

            for comment_row in comments:
                comment = Comment(comment_row)
                author = conn.execute('SELECT * FROM users WHERE id = ?', (comment.user_id,)).fetchone()
                if author:
                    comment.author = User(author)
                card_obj.comments.append(comment)

            column = conn.execute(
                'SELECT is_done FROM columns WHERE id = ?',
                (card_obj.column_id,)
            ).fetchone()
            column_is_done = bool(column['is_done']) if column else False

            return jsonify(card_obj.to_dict(column_is_done=column_is_done))
        return jsonify({'error': 'Card not found'}), 404


@api_bp.route('/cards/<int:card_id>/move', methods=['PUT'])
def move_card(card_id):
    data = request.json
    user_id = data.get('user_id')
    new_column_id = data['column_id']
    new_position = data['position']

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

        if not perm.can_move_card(role, card, user_id):
            return _forbidden('You cannot move this card')

        new_column = conn.execute(
            'SELECT board_id FROM columns WHERE id = ?',
            (new_column_id,)
        ).fetchone()
        if not new_column:
            return jsonify({'error': 'Target column not found'}), 404

        card_board = conn.execute('''
            SELECT b.id FROM boards b
            JOIN columns col ON col.board_id = b.id
            WHERE col.id = ?
        ''', (card['column_id'],)).fetchone()
        if not card_board or new_column['board_id'] != card_board['id']:
            return _forbidden('Cannot move card to another board')

        old_column_id = card['column_id']
        old_position = card['position']

        try:
            if old_column_id == new_column_id:
                if new_position > old_position:
                    conn.execute(
                        '''UPDATE cards SET position = position - 1
                           WHERE column_id = ? AND position > ? AND position <= ? AND id != ?''',
                        (old_column_id, old_position, new_position, card_id)
                    )
                elif new_position < old_position:
                    conn.execute(
                        '''UPDATE cards SET position = position + 1
                           WHERE column_id = ? AND position >= ? AND position < ? AND id != ?''',
                        (old_column_id, new_position, old_position, card_id)
                    )
                conn.execute(
                    'UPDATE cards SET position = ?, updated_at = ? WHERE id = ?',
                    (new_position, datetime.now(), card_id)
                )
            else:
                conn.execute(
                    'UPDATE cards SET position = position - 1 WHERE column_id = ? AND position > ?',
                    (old_column_id, old_position)
                )
                conn.execute(
                    'UPDATE cards SET position = position + 1 WHERE column_id = ? AND position >= ?',
                    (new_column_id, new_position)
                )
                conn.execute(
                    'UPDATE cards SET column_id = ?, position = ?, updated_at = ? WHERE id = ?',
                    (new_column_id, new_position, datetime.now(), card_id)
                )

            return jsonify({'message': 'Card moved successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
