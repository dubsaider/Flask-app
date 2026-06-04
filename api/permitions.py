from flask import jsonify, request
from .init import api_bp
from database import get_db_context

@api_bp.route('/teams/<int:team_id>/user-role/<int:user_id>', methods=['GET'])
def get_user_role(team_id, user_id):
    """Получить роль пользователя в команде"""
    with get_db_context() as conn:
        # Проверяем, является ли пользователь куратором
        team = conn.execute('SELECT curator_id FROM teams WHERE id = ?', (team_id,)).fetchone()
        if team and team['curator_id'] == user_id:
            return jsonify({'role': 'curator'})
        
        # Проверяем, является ли участником команды
        member = conn.execute(
            'SELECT role FROM team_members WHERE team_id = ? AND user_id = ?',
            (team_id, user_id)
        ).fetchone()
        
        if member:
            return jsonify({'role': member['role']})
        
        return jsonify({'role': 'none'})