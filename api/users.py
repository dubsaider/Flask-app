from flask import jsonify, request
from .init import api_bp
from database import get_db_context
from models import User

@api_bp.route('/users', methods=['GET'])
def get_users():
    with get_db_context() as conn:
        users = conn.execute('SELECT * FROM users').fetchall()
        return jsonify([User(user).to_dict() for user in users])

@api_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    with get_db_context() as conn:
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        if user:
            return jsonify(User(user).to_dict())
        return jsonify({'error': 'User not found'}), 404