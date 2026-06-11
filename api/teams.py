from flask import jsonify, request
from .init import api_bp
from .db import session_scope
from .http_helpers import forbidden, not_found, bad_request, access_denied
from models import Team, Board
from models.schema import Team as TeamModel, Board as BoardModel, TeamMember, TeamRole
from .helpers import load_team
from . import permissions as perm
from .role_helpers import seed_default_roles, get_team_role_by_id


@api_bp.route('/teams', methods=['GET', 'POST'])
def teams_handler():
    if request.method == 'POST':
        data = request.json
        user_id = data.get('user_id')
        with session_scope() as session:
            team = TeamModel(name=data['name'], description=data.get('description', ''))
            session.add(team)
            session.flush()
            seed_default_roles(session, team.id)

            if user_id:
                leader_role = (
                    session.query(TeamRole)
                    .filter_by(team_id=team.id, template_key='leader')
                    .first()
                )
                if leader_role:
                    session.merge(TeamMember(team_id=team.id, user_id=user_id, role_id=leader_role.id))

            return jsonify(load_team(session, team).to_dict()), 201

    with session_scope() as session:
        teams = session.query(TeamModel).all()
        return jsonify([load_team(session, team).to_dict() for team in teams])


@api_bp.route('/teams/<int:team_id>', methods=['GET', 'PUT', 'DELETE'])
def team_handler(team_id):
    with session_scope() as session:
        team = session.get(TeamModel, team_id)
        if request.method == 'PUT':
            data = request.json
            user_id = data.get('user_id')
            if not user_id:
                return forbidden('user_id is required')
            if not perm.can_manage_team_members(session, team_id, user_id):
                return forbidden('You cannot edit team settings')
            if not team:
                return not_found('Team not found')

            team.name = data['name']
            team.description = data.get('description', '')
            if 'curator_id' in data:
                team.curator_id = data['curator_id']
            return jsonify(load_team(session, team).to_dict())

        if request.method == 'DELETE':
            data = request.json or {}
            user_id = data.get('user_id')
            if not user_id:
                return forbidden('user_id is required')
            if not team:
                return not_found('Team not found')
            if not perm.can_manage_board(session, team_id, user_id):
                return forbidden('You cannot delete team')
            session.delete(team)
            return '', 204

        if team:
            return jsonify(load_team(session, team).to_dict())
        return not_found('Team not found')


@api_bp.route('/teams/<int:team_id>/members', methods=['POST', 'DELETE'])
def team_members_handler(team_id):
    data = request.json or {}
    user_id = data.get('user_id')
    if not user_id:
        return forbidden('user_id is required')

    if request.method == 'POST':
        with session_scope() as session:
            if not perm.can_manage_team_members(session, team_id, user_id):
                return forbidden('You cannot add team members')

            seed_default_roles(session, team_id)
            role_id = data.get('role_id')
            if not role_id and data.get('role'):
                role_row = (
                    session.query(TeamRole)
                    .filter_by(team_id=team_id, slug=data['role'])
                    .first()
                )
                role_id = role_row.id if role_row else None
            if not role_id:
                default_role = (
                    session.query(TeamRole)
                    .filter_by(team_id=team_id, template_key='developer')
                    .first()
                )
                role_id = default_role.id if default_role else None
            if not role_id:
                return bad_request('Role not found')

            role = get_team_role_by_id(session, team_id, role_id)
            if not role:
                return bad_request('Role not found')

            member_user_id = data.get('member_user_id') or data.get('new_user_id')
            if not member_user_id:
                return bad_request('member_user_id is required')

            existing = (
                session.query(TeamMember)
                .filter_by(team_id=team_id, user_id=member_user_id)
                .first()
            )
            if existing:
                return bad_request('User already in team or not found')

            session.add(TeamMember(team_id=team_id, user_id=member_user_id, role_id=role_id))
            return jsonify({'message': 'Member added'}), 201

    with session_scope() as session:
        if not perm.can_manage_team_members(session, team_id, user_id):
            return forbidden('You cannot remove team members')

        member_user_id = data.get('member_user_id')
        if not member_user_id:
            return bad_request('member_user_id is required')

        member = (
            session.query(TeamMember)
            .filter_by(team_id=team_id, user_id=member_user_id)
            .first()
        )
        if member:
            session.delete(member)
        return '', 204


@api_bp.route('/teams/<int:team_id>/members/<int:member_user_id>', methods=['PUT'])
def update_team_member(team_id, member_user_id):
    data = request.json or {}
    user_id = data.get('user_id')
    role_id = data.get('role_id')

    if not user_id:
        return forbidden('user_id is required')
    if not role_id:
        return bad_request('role_id is required')

    with session_scope() as session:
        if not perm.can_manage_team_members(session, team_id, user_id):
            return forbidden('You cannot change member roles')

        role = get_team_role_by_id(session, team_id, role_id)
        if not role:
            return bad_request('Role not found')

        member = (
            session.query(TeamMember)
            .filter_by(team_id=team_id, user_id=member_user_id)
            .first()
        )
        if not member:
            return not_found('Member not found')

        member.role_id = role_id
        return jsonify({'message': 'Member updated'})


@api_bp.route('/teams/<int:team_id>/boards', methods=['GET'])
def get_team_boards(team_id):
    with session_scope() as session:
        boards = session.query(BoardModel).filter_by(team_id=team_id).all()
        return jsonify([Board(board).to_dict() for board in boards])
