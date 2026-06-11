from flask import jsonify, request
from .init import api_bp
from .db import session_scope
from .http_helpers import forbidden, not_found
from models import Notification
from models.schema import Notification as NotificationModel


def _check_user_access(request_user_id, target_user_id):
    if not request_user_id or int(request_user_id) != int(target_user_id):
        return forbidden('Access denied')
    return None


@api_bp.route('/users/<int:user_id>/notifications', methods=['GET'])
def get_user_notifications(user_id):
    request_user_id = request.args.get('user_id', type=int)
    error = _check_user_access(request_user_id, user_id)
    if error:
        return error

    with session_scope() as session:
        rows = (
            session.query(NotificationModel)
            .filter_by(user_id=user_id)
            .order_by(NotificationModel.created_at.desc(), NotificationModel.id.desc())
            .limit(50)
            .all()
        )
        return jsonify([Notification(row).to_dict() for row in rows])


@api_bp.route('/users/<int:user_id>/notifications/unread-count', methods=['GET'])
def get_unread_count(user_id):
    request_user_id = request.args.get('user_id', type=int)
    error = _check_user_access(request_user_id, user_id)
    if error:
        return error

    with session_scope() as session:
        count = (
            session.query(NotificationModel)
            .filter_by(user_id=user_id, is_read=False)
            .count()
        )
        return jsonify({'count': count})


@api_bp.route('/users/<int:user_id>/notifications/read-all', methods=['PUT'])
def mark_all_read(user_id):
    data = request.json or {}
    error = _check_user_access(data.get('user_id'), user_id)
    if error:
        return error

    with session_scope() as session:
        session.query(NotificationModel).filter_by(
            user_id=user_id, is_read=False
        ).update({NotificationModel.is_read: True}, synchronize_session=False)
        return jsonify({'message': 'All notifications marked as read'})


@api_bp.route('/notifications/<int:notification_id>/read', methods=['PUT'])
def mark_notification_read(notification_id):
    data = request.json or {}
    user_id = data.get('user_id')
    if not user_id:
        return forbidden('user_id is required')

    with session_scope() as session:
        row = session.get(NotificationModel, notification_id)

        if not row:
            return not_found('Notification not found')
        if row.user_id != user_id:
            return forbidden('Access denied')

        row.is_read = True
        return jsonify(Notification(row).to_dict())
