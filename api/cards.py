from flask import jsonify, request
from datetime import datetime
from .init import api_bp
from database import get_db_context
from models import Card, User

@api_bp.route('/cards', methods=['POST'])
def create_card():
    data = request.json
    with get_db_context() as conn:
        max_pos = conn.execute(
            'SELECT COALESCE(MAX(position), -1) as max_pos FROM cards WHERE column_id = ?',
            (data['column_id'],)
        ).fetchone()['max_pos']
        
        cursor = conn.execute(
            'INSERT INTO cards (title, description, position, column_id, assignee_id, priority) VALUES (?, ?, ?, ?, ?, ?)',
            (data['title'], data.get('description', ''), max_pos + 1, data['column_id'], 
             data.get('assignee_id'), data.get('priority', 'medium'))
        )
        card = conn.execute('SELECT * FROM cards WHERE id = ?', (cursor.lastrowid,)).fetchone()
        return jsonify(Card(card).to_dict()), 201

@api_bp.route('/cards/<int:card_id>', methods=['GET', 'PUT', 'DELETE'])
def card_handler(card_id):
    with get_db_context() as conn:
        if request.method == 'PUT':
            data = request.json
            conn.execute(
                '''UPDATE cards 
                   SET title = ?, description = ?, assignee_id = ?, priority = ?, updated_at = ? 
                   WHERE id = ?''',
                (data['title'], data.get('description', ''), data.get('assignee_id'),
                 data.get('priority', 'medium'), datetime.now(), card_id)
            )
            card = conn.execute('SELECT * FROM cards WHERE id = ?', (card_id,)).fetchone()
            if card:
                return jsonify(Card(card).to_dict())
            return jsonify({'error': 'Card not found'}), 404
            
        elif request.method == 'DELETE':
            conn.execute('DELETE FROM cards WHERE id = ?', (card_id,))
            return '', 204
        
        card = conn.execute('SELECT * FROM cards WHERE id = ?', (card_id,)).fetchone()
        if card:
            card_obj = Card(card)
            if card_obj.assignee_id:
                assignee = conn.execute(
                    'SELECT * FROM users WHERE id = ?',
                    (card_obj.assignee_id,)
                ).fetchone()
                if assignee:
                    card_obj.assignee = User(assignee)
            return jsonify(card_obj.to_dict())
        return jsonify({'error': 'Card not found'}), 404

@api_bp.route('/cards/<int:card_id>/move', methods=['PUT'])
def move_card(card_id):
    """Перемещение карточки между колонками и изменение позиции"""
    data = request.json
    new_column_id = data['column_id']
    new_position = data['position']
    
    with get_db_context() as conn:
        # Получаем текущую карточку
        card = conn.execute('SELECT * FROM cards WHERE id = ?', (card_id,)).fetchone()
        if not card:
            return jsonify({'error': 'Card not found'}), 404
        
        old_column_id = card['column_id']
        old_position = card['position']
        
        # Проверяем, существует ли новая колонка
        column = conn.execute('SELECT * FROM columns WHERE id = ?', (new_column_id,)).fetchone()
        if not column:
            return jsonify({'error': 'Column not found'}), 404
        
        # Если позиция та же и колонка та же - ничего не делаем
        if old_column_id == new_column_id and old_position == new_position:
            return jsonify({'message': 'Card already in this position'})
        
        try:
            if old_column_id == new_column_id:
                # Перемещение в пределах одной колонки
                if new_position > old_position:
                    # Двигаем вниз: сдвигаем карточки между старой и новой позицией вверх
                    conn.execute(
                        '''UPDATE cards 
                           SET position = position - 1 
                           WHERE column_id = ? 
                           AND position > ? 
                           AND position <= ? 
                           AND id != ?''',
                        (old_column_id, old_position, new_position, card_id)
                    )
                else:
                    # Двигаем вверх: сдвигаем карточки между новой и старой позицией вниз
                    conn.execute(
                        '''UPDATE cards 
                           SET position = position + 1 
                           WHERE column_id = ? 
                           AND position >= ? 
                           AND position < ? 
                           AND id != ?''',
                        (old_column_id, new_position, old_position, card_id)
                    )
                
                # Обновляем позицию перемещаемой карточки
                conn.execute(
                    'UPDATE cards SET position = ?, updated_at = ? WHERE id = ?',
                    (new_position, datetime.now(), card_id)
                )
            else:
                # Перемещение между разными колонками
                
                # 1. Сдвигаем карточки в старой колонке (убираем карточку)
                conn.execute(
                    '''UPDATE cards 
                       SET position = position - 1 
                       WHERE column_id = ? 
                       AND position > ?''',
                    (old_column_id, old_position)
                )
                
                # 2. Сдвигаем карточки в новой колонке (освобождаем место)
                conn.execute(
                    '''UPDATE cards 
                       SET position = position + 1 
                       WHERE column_id = ? 
                       AND position >= ?''',
                    (new_column_id, new_position)
                )
                
                # 3. Перемещаем карточку в новую колонку
                conn.execute(
                    '''UPDATE cards 
                       SET column_id = ?, position = ?, updated_at = ? 
                       WHERE id = ?''',
                    (new_column_id, new_position, datetime.now(), card_id)
                )
            
            return jsonify({'message': 'Card moved successfully'})
            
        except Exception as e:
            print(f"Error moving card: {str(e)}")
            return jsonify({'error': str(e)}), 500