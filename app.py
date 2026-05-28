from flask import Flask, jsonify, request
from flask import render_template
from database import init_db, get_db_context
from models import User, Team, Board

app = Flask(__name__)

# Инициализация базы данных при запуске
with app.app_context():
    init_db()


# ============ Page Endpoints ============

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/boards')
def boards_list():
    """Страница со списком досок"""
    return render_template('boards.html')

@app.route('/boards/<int:board_id>')
def board_detail(board_id):
    """Страница конкретной доски"""
    return render_template('board_detail.html', board_id=board_id)

@app.route('/teams')
def teams_list():
    """Страница со списком команд"""
    return render_template('teams.html')

@app.route('/teams/<int:team_id>')
def team_detail(team_id):
    """Страница конкретной команды"""
    return render_template('team_detail.html', team_id=team_id)


# ============ API Endpoints ============

# Users API
@app.route('/api/users', methods=['GET'])
def get_users():
    """Получить всех пользователей"""
    with get_db_context() as conn:
        users = conn.execute('SELECT * FROM users').fetchall()
        return jsonify([User(user).to_dict() for user in users])

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Получить пользователя по ID"""
    with get_db_context() as conn:
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        if user:
            return jsonify(User(user).to_dict())
        return jsonify({'error': 'User not found'}), 404

# Teams API
@app.route('/api/teams', methods=['GET'])
def get_teams():
    """Получить все команды"""
    with get_db_context() as conn:
        teams = conn.execute('SELECT * FROM teams').fetchall()
        result = []
        for team_row in teams:
            team = Team(team_row)
            # Получаем членов команды
            members = conn.execute('''
                SELECT u.*, tm.role 
                FROM users u 
                JOIN team_members tm ON u.id = tm.user_id 
                WHERE tm.team_id = ?
            ''', (team.id,)).fetchall()
            team.members = [User(m) for m in members]
            result.append(team.to_dict())
        return jsonify(result)

@app.route('/api/teams/<int:team_id>', methods=['GET'])
def get_team(team_id):
    """Получить команду по ID"""
    with get_db_context() as conn:
        team_row = conn.execute('SELECT * FROM teams WHERE id = ?', (team_id,)).fetchone()
        if team_row:
            team = Team(team_row)
            members = conn.execute('''
                SELECT u.*, tm.role 
                FROM users u 
                JOIN team_members tm ON u.id = tm.user_id 
                WHERE tm.team_id = ?
            ''', (team_id,)).fetchall()
            team.members = [User(m) for m in members]
            return jsonify(team.to_dict())
        return jsonify({'error': 'Team not found'}), 404

# Boards API
@app.route('/api/boards', methods=['GET'])
def get_boards():
    """Получить все доски"""
    with get_db_context() as conn:
        boards = conn.execute('SELECT * FROM boards').fetchall()
        return jsonify([Board(board).to_dict() for board in boards])

@app.route('/api/boards/<int:board_id>', methods=['GET'])
def get_board(board_id):
    """Получить доску по ID"""
    with get_db_context() as conn:
        board = conn.execute('SELECT * FROM boards WHERE id = ?', (board_id,)).fetchone()
        if board:
            return jsonify(Board(board).to_dict())
        return jsonify({'error': 'Board not found'}), 404

@app.route('/api/teams/<int:team_id>/boards', methods=['GET'])
def get_team_boards(team_id):
    """Получить все доски команды"""
    with get_db_context() as conn:
        boards = conn.execute('SELECT * FROM boards WHERE team_id = ?', (team_id,)).fetchall()
        return jsonify([Board(board).to_dict() for board in boards])

if __name__ == '__main__':
    app.run(debug=True, port=5000)