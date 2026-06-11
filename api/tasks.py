from flask import jsonify
from datetime import datetime
from sqlalchemy import func
from .init import api_bp
from .db import session_scope
from .http_helpers import forbidden
from models import User
from models.schema import (
    Card as CardModel,
    Column as ColumnModel,
    Board as BoardModel,
    Team as TeamModel,
    TeamMember,
    TeamRole,
    User as UserModel,
    Comment as CommentModel,
)
from .helpers import user_has_team_access
from . import permissions as perm
from .card_helpers import workflow_fields, is_in_progress


def _card_context(session, card, column_title, column_is_done, board_id, board_title, team_id, team_name):
    assignee = None
    if card.assignee_id:
        user = session.get(UserModel, card.assignee_id)
        if user:
            assignee = User(user).to_dict()

    comments_count = session.query(func.count(CommentModel.id)).filter_by(card_id=card.id).scalar() or 0
    wf = workflow_fields(card.status, bool(column_is_done))

    deadline = card.deadline
    created = card.created_at
    updated = card.updated_at

    return {
        'id': card.id,
        'title': card.title,
        'description': card.description,
        'position': card.position,
        'column_id': card.column_id,
        'column_title': column_title,
        'column_is_done': bool(column_is_done),
        'board_id': board_id,
        'board_title': board_title,
        'team_id': team_id,
        'team_name': team_name,
        'assignee_id': card.assignee_id,
        'assignee': assignee,
        'created_by': card.created_by,
        'priority': card.priority,
        'status': wf['status'],
        'workflow_status': wf['workflow_status'],
        'is_completed': wf['is_completed'],
        'deadline': deadline.isoformat() if hasattr(deadline, 'isoformat') else deadline,
        'created_at': created.isoformat() if hasattr(created, 'isoformat') else created,
        'updated_at': updated.isoformat() if hasattr(updated, 'isoformat') else updated,
        'comments_count': comments_count,
    }


def _is_overdue(deadline, status, column_is_done):
    if not is_in_progress(status, column_is_done):
        return False
    if not deadline:
        return False
    try:
        if hasattr(deadline, 'isoformat'):
            deadline_dt = deadline
        else:
            deadline_dt = datetime.fromisoformat(str(deadline).replace(' ', 'T'))
        return deadline_dt < datetime.now()
    except ValueError:
        return False


def _query_team_cards(session, team_ids, assignee_id=None):
    query = (
        session.query(
            CardModel,
            ColumnModel.title,
            ColumnModel.is_done,
            ColumnModel.board_id,
            BoardModel.title,
            BoardModel.team_id,
            TeamModel.name,
        )
        .join(ColumnModel, CardModel.column_id == ColumnModel.id)
        .join(BoardModel, ColumnModel.board_id == BoardModel.id)
        .join(TeamModel, BoardModel.team_id == TeamModel.id)
        .filter(BoardModel.team_id.in_(team_ids))
    )
    if assignee_id is not None:
        query = query.filter(CardModel.assignee_id == assignee_id)
    return query.order_by(BoardModel.title, ColumnModel.position, CardModel.position)


@api_bp.route('/users/<int:user_id>/tasks', methods=['GET'])
def get_user_tasks(user_id):
    """Задачи пользователя (назначенные ему) по всем доступным доскам"""
    with session_scope() as session:
        teams = session.query(TeamModel).order_by(TeamModel.name).all()
        team_ids = [team.id for team in teams if user_has_team_access(session, team, user_id)]

        if not team_ids:
            return jsonify([])

        rows = _query_team_cards(session, team_ids, assignee_id=user_id).all()
        return jsonify([
            _card_context(session, card, col_title, col_done, board_id, board_title, team_id, team_name)
            for card, col_title, col_done, board_id, board_title, team_id, team_name in rows
        ])


@api_bp.route('/users/<int:user_id>/leader-dashboard', methods=['GET'])
def get_leader_dashboard(user_id):
    """Дашборд для руководителя — статистика по командам"""
    with session_scope() as session:
        leader_teams = (
            session.query(TeamModel)
            .join(TeamMember, TeamModel.id == TeamMember.team_id)
            .join(TeamRole, TeamMember.role_id == TeamRole.id)
            .filter(TeamMember.user_id == user_id)
            .distinct()
            .order_by(TeamModel.name)
            .all()
        )

        accessible_teams = [
            team for team in leader_teams
            if perm.can_view_dashboard(session, team.id, user_id)
        ]

        if not accessible_teams:
            return forbidden('Dashboard access denied')

        result = []
        for team in accessible_teams:
            team_id = team.id

            rows = _query_team_cards(session, [team_id]).all()
            card_items = [
                _card_context(session, card, col_title, col_done, board_id, board_title, tid, team_name)
                for card, col_title, col_done, board_id, board_title, tid, team_name in rows
            ]

            by_priority = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
            by_workflow = {'active': 0, 'completed': 0, 'archived': 0}
            by_column = {}
            by_assignee = {}
            overdue = []
            unassigned = []

            for card in card_items:
                by_priority[card['priority']] = by_priority.get(card['priority'], 0) + 1
                ws = card['workflow_status']
                by_workflow[ws] = by_workflow.get(ws, 0) + 1

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
                    if ws == 'active':
                        by_assignee[aid]['active'] += 1
                    if _is_overdue(card['deadline'], card['status'], card['column_is_done']):
                        by_assignee[aid]['overdue'] += 1

                if _is_overdue(card['deadline'], card['status'], card['column_is_done']):
                    overdue.append(card)

            members = (
                session.query(UserModel.id, UserModel.username, TeamRole.slug, TeamRole.name)
                .join(TeamMember, UserModel.id == TeamMember.user_id)
                .join(TeamRole, TeamMember.role_id == TeamRole.id)
                .filter(TeamMember.team_id == team_id)
                .all()
            )

            boards = session.query(BoardModel.id, BoardModel.title).filter_by(team_id=team_id).all()

            result.append({
                'team': {
                    'id': team_id,
                    'name': team.name,
                    'description': team.description,
                },
                'summary': {
                    'total': len(card_items),
                    'active': by_workflow.get('active', 0),
                    'completed': by_workflow.get('completed', 0),
                    'archived': by_workflow.get('archived', 0),
                    'overdue': len(overdue),
                    'unassigned': len(unassigned),
                },
                'by_priority': by_priority,
                'by_status': by_workflow,
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
                    {'id': m[0], 'username': m[1], 'role': m[2]}
                    for m in members
                ],
                'boards': [{'id': b[0], 'title': b[1]} for b in boards],
                'overdue_tasks': overdue[:10],
                'unassigned_tasks': unassigned[:10],
            })

        return jsonify(result)
