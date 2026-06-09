from flask import jsonify, request
from .init import api_bp
from database import get_db_context
from models import Notification


def _forbidden(message):
    return jsonify({'error': message}), 403


def _check_user_access(request_user_id, target_user_id):
    if not request_user_id or int(request_user_id) != int(target_user_id):
        return _forbidden('Access denied')
    return None


@api_bp.route('/users/<int:user_id>/notifications', methods=['GET'])
def get_user_notifications(user_id):
    request_user_id = request.args.get('user_id', type=int)
    error = _check_user_access(request_user_id, user_id)
    if error:
        return error

    with get_db_context() as conn:
        rows = conn.execute('''
            SELECT * FROM notifications
            WHERE user_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT 50
        ''', (user_id,)).fetchall()

        return jsonify([Notification(row).to_dict() for row in rows])


@api_bp.route('/users/<int:user_id>/notifications/unread-count', methods=['GET'])
def get_unread_count(user_id):
    request_user_id = request.args.get('user_id', type=int)
    error = _check_user_access(request_user_id, user_id)
    if error:
        return error

    with get_db_context() as conn:
        count = conn.execute('''
            SELECT COUNT(*) AS cnt FROM notifications
            WHERE user_id = ? AND is_read = 0
        ''', (user_id,)).fetchone()['cnt']

        return jsonify({'count': count})


@api_bp.route('/users/<int:user_id>/notifications/read-all', methods=['PUT'])
def mark_all_read(user_id):
    data = request.json or {}
    error = _check_user_access(data.get('user_id'), user_id)
    if error:
        return error

    with get_db_context() as conn:
        conn.execute(
            'UPDATE notifications SET is_read = 1 WHERE user_id = ? AND is_read = 0',
            (user_id,)
        )
        return jsonify({'message': 'All notifications marked as read'})


@api_bp.route('/notifications/<int:notification_id>/read', methods=['PUT'])
def mark_notification_read(notification_id):
    data = request.json or {}
    user_id = data.get('user_id')
    if not user_id:
        return _forbidden('user_id is required')

    with get_db_context() as conn:
        row = conn.execute(
            'SELECT * FROM notifications WHERE id = ?',
            (notification_id,)
        ).fetchone()

        if not row:
            return jsonify({'error': 'Notification not found'}), 404
        if row['user_id'] != user_id:
            return _forbidden('Access denied')

        conn.execute(
            'UPDATE notifications SET is_read = 1 WHERE id = ?',
            (notification_id,)
        )
        updated = conn.execute(
            'SELECT * FROM notifications WHERE id = ?',
            (notification_id,)
        ).fetchone()
        return jsonify(Notification(updated).to_dict())
