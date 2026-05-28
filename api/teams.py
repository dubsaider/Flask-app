from flask import jsonify, request
from .init import api_bp
from database import get_db_context
from models import User, Team, Board  # Добавляем импорт Board

@api_bp.route('/teams', methods=['GET', 'POST'])
def teams_handler():
    if request.method == 'POST':
        data = request.json
        with get_db_context() as conn:
            cursor = conn.execute(
                'INSERT INTO teams (name, description) VALUES (?, ?)',
                (data['name'], data.get('description', ''))
            )
            team = conn.execute('SELECT * FROM teams WHERE id = ?', (cursor.lastrowid,)).fetchone()
            return jsonify(Team(team).to_dict()), 201
    
    with get_db_context() as conn:
        teams = conn.execute('SELECT * FROM teams').fetchall()
        result = []
        for team_row in teams:
            team = Team(team_row)
            members = conn.execute('''
                SELECT u.*, tm.role 
                FROM users u 
                JOIN team_members tm ON u.id = tm.user_id 
                WHERE tm.team_id = ?
            ''', (team.id,)).fetchall()
            team.members = [User(m) for m in members]
            result.append(team.to_dict())
        return jsonify(result)

@api_bp.route('/teams/<int:team_id>', methods=['GET', 'PUT', 'DELETE'])
def team_handler(team_id):
    with get_db_context() as conn:
        if request.method == 'PUT':
            data = request.json
            conn.execute(
                'UPDATE teams SET name = ?, description = ? WHERE id = ?',
                (data['name'], data.get('description', ''), team_id)
            )
            team = conn.execute('SELECT * FROM teams WHERE id = ?', (team_id,)).fetchone()
            if team:
                return jsonify(Team(team).to_dict())
            return jsonify({'error': 'Team not found'}), 404
            
        elif request.method == 'DELETE':
            conn.execute('DELETE FROM teams WHERE id = ?', (team_id,))
            return '', 204
        
        team = conn.execute('SELECT * FROM teams WHERE id = ?', (team_id,)).fetchone()
        if team:
            team_obj = Team(team)
            members = conn.execute('''
                SELECT u.*, tm.role 
                FROM users u 
                JOIN team_members tm ON u.id = tm.user_id 
                WHERE tm.team_id = ?
            ''', (team_id,)).fetchall()
            team_obj.members = [User(m) for m in members]
            return jsonify(team_obj.to_dict())
        return jsonify({'error': 'Team not found'}), 404

@api_bp.route('/teams/<int:team_id>/members', methods=['POST', 'DELETE'])
def team_members_handler(team_id):
    if request.method == 'POST':
        data = request.json
        with get_db_context() as conn:
            try:
                conn.execute(
                    'INSERT INTO team_members (team_id, user_id, role) VALUES (?, ?, ?)',
                    (team_id, data['user_id'], data.get('role', 'member'))
                )
                return jsonify({'message': 'Member added'}), 201
            except:
                return jsonify({'error': 'User already in team or not found'}), 400
    
    elif request.method == 'DELETE':
        data = request.json
        with get_db_context() as conn:
            conn.execute(
                'DELETE FROM team_members WHERE team_id = ? AND user_id = ?',
                (team_id, data['user_id'])
            )
            return '', 204

@api_bp.route('/teams/<int:team_id>/boards', methods=['GET'])
def get_team_boards(team_id):
    with get_db_context() as conn:
        boards = conn.execute('SELECT * FROM boards WHERE team_id = ?', (team_id,)).fetchall()
        return jsonify([Board(board).to_dict() for board in boards])