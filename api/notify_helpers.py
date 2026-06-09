"""Создание in-app уведомлений."""


def create_notification(conn, user_id, message, board_id=None, card_id=None):
    if not user_id or not message:
        return
    conn.execute(
        '''INSERT INTO notifications (user_id, message, board_id, card_id)
           VALUES (?, ?, ?, ?)''',
        (user_id, message, board_id, card_id)
    )


def get_username(conn, user_id):
    row = conn.execute('SELECT username FROM users WHERE id = ?', (user_id,)).fetchone()
    return row['username'] if row else 'Пользователь'


def get_card_context(conn, card_id):
    return conn.execute('''
        SELECT c.id, c.title, c.assignee_id,
               col.board_id, b.title AS board_title
        FROM cards c
        JOIN columns col ON c.column_id = col.id
        JOIN boards b ON col.board_id = b.id
        WHERE c.id = ?
    ''', (card_id,)).fetchone()


def notify_assignee(conn, card_id, assignee_id, actor_id, action='assigned'):
    if not assignee_id or assignee_id == actor_id:
        return

    ctx = get_card_context(conn, card_id)
    if not ctx:
        return

    actor = get_username(conn, actor_id)
    if action == 'assigned':
        message = f'{actor} назначил вам задачу «{ctx["title"]}» ({ctx["board_title"]})'
    else:
        message = f'{actor} переназначил вам задачу «{ctx["title"]}» ({ctx["board_title"]})'

    create_notification(
        conn, assignee_id, message,
        board_id=ctx['board_id'], card_id=ctx['id']
    )


def notify_comment(conn, card_id, commenter_id):
    ctx = get_card_context(conn, card_id)
    if not ctx or not ctx['assignee_id']:
        return
    if ctx['assignee_id'] == commenter_id:
        return

    author = get_username(conn, commenter_id)
    message = f'{author} оставил комментарий к задаче «{ctx["title"]}» ({ctx["board_title"]})'
    create_notification(
        conn, ctx['assignee_id'], message,
        board_id=ctx['board_id'], card_id=ctx['id']
    )
