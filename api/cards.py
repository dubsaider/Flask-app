from flask import jsonify, request
from datetime import datetime
from .init import api_bp
from database import get_db_context
from models import Card, User, Comment

@api_bp.route('/cards', methods=['POST'])
def create_card():
    data = request.json
    with get_db_context() as conn:
        # Проверяем, что создатель - руководитель команды
        board = conn.execute('''
            SELECT b.*, tm.role 
            FROM boards b
            JOIN columns c ON b.id = c.board_id
            JOIN team_members tm ON b.team_id = tm.team_id
            WHERE c.id = ? AND tm.user_id = ? AND tm.role = 'leader'
        ''', (data['column_id'], data.get('created_by'))).fetchone()
        
        # Если нет прав, но в данных указан created_by - выдаем ошибку
        if data.get('created_by') and not board:
            return jsonify({'error': 'Only team leader can create tasks'}), 403
        
        max_pos = conn.execute(
            'SELECT COALESCE(MAX(position), -1) as max_pos FROM cards WHERE column_id = ?',
            (data['column_id'],)
        ).fetchone()['max_pos']
        
        cursor = conn.execute(
            '''INSERT INTO cards (title, description, position, column_id, assignee_id, created_by, priority, deadline) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (data['title'], data.get('description', ''), max_pos + 1, data['column_id'], 
             data.get('assignee_id'), data.get('created_by'), data.get('priority', 'medium'),
             data.get('deadline'))
        )
        card = conn.execute('SELECT * FROM cards WHERE id = ?', (cursor.lastrowid,)).fetchone()
        return jsonify(Card(card).to_dict()), 201

@api_bp.route('/cards/<int:card_id>', methods=['GET', 'PUT', 'DELETE'])
def card_handler(card_id):
    with get_db_context() as conn:
        if request.method == 'PUT':
            data = request.json
            existing = conn.execute('SELECT * FROM cards WHERE id = ?', (card_id,)).fetchone()
            if not existing:
                return jsonify({'error': 'Card not found'}), 404
            
            # Проверяем права: только руководитель может менять assignee
            if 'assignee_id' in data and data.get('user_id'):
                team_member = conn.execute('''
                    SELECT tm.role 
                    FROM cards c
                    JOIN columns col ON c.column_id = col.id
                    JOIN boards b ON col.board_id = b.id
                    JOIN team_members tm ON b.team_id = tm.team_id
                    WHERE c.id = ? AND tm.user_id = ?
                ''', (card_id, data['user_id'])).fetchone()
                
                if team_member and team_member['role'] != 'leader':
                    return jsonify({'error': 'Only team leader can change assignee'}), 403
            
            assignee_id = data['assignee_id'] if 'assignee_id' in data else existing['assignee_id']
            
            conn.execute(
                '''UPDATE cards 
                   SET title = ?, description = ?, assignee_id = ?, priority = ?, 
                       status = ?, deadline = ?, updated_at = ? 
                   WHERE id = ?''',
                (data['title'], data.get('description', ''), assignee_id,
                 data.get('priority', 'medium'), data.get('status', 'active'),
                 data.get('deadline'), datetime.now(), card_id)
            )
            card = conn.execute('SELECT * FROM cards WHERE id = ?', (card_id,)).fetchone()
            if card:
                return jsonify(Card(card).to_dict())
            return jsonify({'error': 'Card not found'}), 404
            
        elif request.method == 'DELETE':
            conn.execute('DELETE FROM cards WHERE id = ?', (card_id,))
            return '', 204
        
        # GET запрос с полной информацией
        card = conn.execute('SELECT * FROM cards WHERE id = ?', (card_id,)).fetchone()
        if card:
            card_obj = Card(card)
            
            # Загружаем исполнителя
            if card_obj.assignee_id:
                assignee = conn.execute('SELECT * FROM users WHERE id = ?', (card_obj.assignee_id,)).fetchone()
                if assignee:
                    card_obj.assignee = User(assignee)
            
            # Загружаем создателя
            if card_obj.created_by:
                creator = conn.execute('SELECT * FROM users WHERE id = ?', (card_obj.created_by,)).fetchone()
                if creator:
                    card_obj.creator = User(creator)
            
            # Загружаем комментарии
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
            
            return jsonify(card_obj.to_dict())
        return jsonify({'error': 'Card not found'}), 404

@api_bp.route('/cards/<int:card_id>/move', methods=['PUT'])
def move_card(card_id):
    """Перемещение карточки между колонками"""
    data = request.json
    new_column_id = data['column_id']
    new_position = data['position']
    
    with get_db_context() as conn:
        card = conn.execute('SELECT * FROM cards WHERE id = ?', (card_id,)).fetchone()
        if not card:
            return jsonify({'error': 'Card not found'}), 404
        
        old_column_id = card['column_id']
        old_position = card['position']
        
        try:
            if old_column_id == new_column_id:
                # Перемещение в пределах одной колонки
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
                conn.execute('UPDATE cards SET position = ?, updated_at = ? WHERE id = ?',
                           (new_position, datetime.now(), card_id))
            else:
                # Перемещение между колонками
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
            print(f"Error moving card: {e}")
            return jsonify({'error': str(e)}), 500