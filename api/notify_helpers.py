"""Создание in-app уведомлений."""
from models.schema import Card, Column, Board, Notification, User


def create_notification(session, user_id, message, board_id=None, card_id=None):
    if not user_id or not message:
        return
    session.add(Notification(
        user_id=user_id,
        message=message,
        board_id=board_id,
        card_id=card_id,
    ))


def get_username(session, user_id):
    user = session.get(User, user_id)
    return user.username if user else 'Пользователь'


def get_card_context(session, card_id):
    row = (
        session.query(
            Card.id,
            Card.title,
            Card.assignee_id,
            Column.board_id,
            Board.title.label('board_title'),
        )
        .join(Column, Card.column_id == Column.id)
        .join(Board, Column.board_id == Board.id)
        .filter(Card.id == card_id)
        .first()
    )
    if not row:
        return None
    return {
        'id': row.id,
        'title': row.title,
        'assignee_id': row.assignee_id,
        'board_id': row.board_id,
        'board_title': row.board_title,
    }


def notify_assignee(session, card_id, assignee_id, actor_id, action='assigned'):
    if not assignee_id or assignee_id == actor_id:
        return

    ctx = get_card_context(session, card_id)
    if not ctx:
        return

    actor = get_username(session, actor_id)
    if action == 'assigned':
        message = f'{actor} назначил вам задачу «{ctx["title"]}» ({ctx["board_title"]})'
    else:
        message = f'{actor} переназначил вам задачу «{ctx["title"]}» ({ctx["board_title"]})'

    create_notification(
        session, assignee_id, message,
        board_id=ctx['board_id'], card_id=ctx['id'],
    )


def notify_comment(session, card_id, commenter_id):
    ctx = get_card_context(session, card_id)
    if not ctx or not ctx['assignee_id']:
        return
    if ctx['assignee_id'] == commenter_id:
        return

    author = get_username(session, commenter_id)
    message = f'{author} оставил комментарий к задаче «{ctx["title"]}» ({ctx["board_title"]})'
    create_notification(
        session, ctx['assignee_id'], message,
        board_id=ctx['board_id'], card_id=ctx['id'],
    )
