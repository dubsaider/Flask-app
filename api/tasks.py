from flask import jsonify
from datetime import datetime
from .init import api_bp
from database import get_db_context
from models import User
from .helpers import user_has_team_access
from . import permissions as perm


def _card_context(conn, card_row):
    assignee = None
    if card_row['assignee_id']:
        user = conn.execute(
            'SELECT * FROM users WHERE id = ?',
            (card_row['assignee_id'],)
        ).fetchone()
        if user:
            assignee = User(user).to_dict()

    comments_count = conn.execute(
        'SELECT COUNT(*) as cnt FROM comments WHERE card_id = ?',
        (card_row['id'],)
    ).fetchone()['cnt']

    return {
        'id': card_row['id'],
        'title': card_row['title'],
        'description': card_row['description'],
        'position': card_row['position'],
        'column_id': card_row['column_id'],
        'column_title': card_row['column_title'],
        'board_id': card_row['board_id'],
        'board_title': card_row['board_title'],
        'team_id': card_row['team_id'],
        'team_name': card_row['team_name'],
        'assignee_id': card_row['assignee_id'],
        'assignee': assignee,
        'created_by': card_row['created_by'],
        'priority': card_row['priority'],
        'status': card_row['status'],
        'deadline': card_row['deadline'],
        'created_at': card_row['created_at'],
        'updated_at': card_row['updated_at'],
        'comments_count': comments_count,
    }


def _is_overdue(deadline_str):
    if not deadline_str:
        return False
    try:
        deadline = datetime.fromisoformat(deadline_str.replace(' ', 'T'))
        return deadline < datetime.now()
    except ValueError:
        return False


@api_bp.route('/users/<int:user_id>/tasks', methods=['GET'])
def get_user_tasks(user_id):
    """Задачи пользователя (назначенные ему) по всем доступным доскам"""
    with get_db_context() as conn:
        teams = conn.execute('SELECT * FROM teams ORDER BY name').fetchall()
        team_ids = [
            team['id'] for team in teams
            if user_has_team_access(conn, team, user_id)
        ]

        if not team_ids:
            return jsonify([])

        placeholders = ','.join('?' * len(team_ids))
        rows = conn.execute(f'''
            SELECT c.*,
                   col.title AS column_title,
                   col.board_id,
                   b.title AS board_title,
                   b.team_id,
                   t.name AS team_name
            FROM cards c
            JOIN columns col ON c.column_id = col.id
            JOIN boards b ON col.board_id = b.id
            JOIN teams t ON b.team_id = t.id
            WHERE b.team_id IN ({placeholders}) AND c.assignee_id = ?
            ORDER BY b.title, col.position, c.position
        ''', (*team_ids, user_id)).fetchall()

        return jsonify([_card_context(conn, row) for row in rows])


@api_bp.route('/users/<int:user_id>/leader-dashboard', methods=['GET'])
def get_leader_dashboard(user_id):
    """Дашборд для руководителя — статистика по командам"""
    with get_db_context() as conn:
        leader_teams = conn.execute('''
            SELECT t.*
            FROM teams t
            JOIN team_members tm ON t.id = tm.team_id
            WHERE tm.user_id = ? AND tm.role = 'leader'
            ORDER BY t.name
        ''', (user_id,)).fetchall()

        if not leader_teams:
            return jsonify({'error': 'Not a team leader'}), 403

        result = []
        for team in leader_teams:
            team_id = team['id']

            cards = conn.execute('''
                SELECT c.*,
                       col.title AS column_title,
                       col.board_id,
                       b.title AS board_title,
                       b.team_id,
                       t.name AS team_name
                FROM cards c
                JOIN columns col ON c.column_id = col.id
                JOIN boards b ON col.board_id = b.id
                JOIN teams t ON b.team_id = t.id
                WHERE b.team_id = ?
            ''', (team_id,)).fetchall()

            card_items = [_card_context(conn, row) for row in cards]

            by_priority = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
            by_status = {'active': 0, 'completed': 0, 'archived': 0}
            by_column = {}
            by_assignee = {}
            overdue = []
            unassigned = []

            for card in card_items:
                by_priority[card['priority']] = by_priority.get(card['priority'], 0) + 1
                by_status[card['status']] = by_status.get(card['status'], 0) + 1

                col_key = card['column_title']
                by_column[col_key] = by_column.get(col_key, 0) + 1

                if not card['assignee_id']:
                    unassigned.append(card)
                else:
                    aid = card['assignee_id']
                    if aid not in by_assignee:
                        by_assignee[aid] = {
                            'user_id': aid,
                            'username': card['assignee']['username'],
                            'total': 0,
                            'overdue': 0,
                            'active': 0,
                        }
                    by_assignee[aid]['total'] += 1
                    if card['status'] == 'active':
                        by_assignee[aid]['active'] += 1
                    if _is_overdue(card['deadline']) and card['status'] == 'active':
                        by_assignee[aid]['overdue'] += 1

                if _is_overdue(card['deadline']) and card['status'] == 'active':
                    overdue.append(card)

            members = conn.execute('''
                SELECT u.id, u.username, tm.role
                FROM users u
                JOIN team_members tm ON u.id = tm.user_id
                WHERE tm.team_id = ?
            ''', (team_id,)).fetchall()

            boards = conn.execute(
                'SELECT id, title FROM boards WHERE team_id = ?',
                (team_id,)
            ).fetchall()

            result.append({
                'team': {
                    'id': team_id,
                    'name': team['name'],
                    'description': team['description'],
                },
                'summary': {
                    'total': len(card_items),
                    'active': by_status.get('active', 0),
                    'completed': by_status.get('completed', 0),
                    'archived': by_status.get('archived', 0),
                    'overdue': len(overdue),
                    'unassigned': len(unassigned),
                },
                'by_priority': by_priority,
                'by_status': by_status,
                'by_column': [
                    {'column': name, 'count': count}
                    for name, count in sorted(by_column.items())
                ],
                'by_assignee': sorted(
                    by_assignee.values(),
                    key=lambda x: x['total'],
                    reverse=True
                ),
                'members': [
                    {'id': m['id'], 'username': m['username'], 'role': m['role']}
                    for m in members
                ],
                'boards': [{'id': b['id'], 'title': b['title']} for b in boards],
                'overdue_tasks': overdue[:10],
                'unassigned_tasks': unassigned[:10],
            })

        return jsonify(result)
