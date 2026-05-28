from flask import render_template
from .init import web_bp

@web_bp.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@web_bp.route('/boards')
def boards_list():
    """Страница со списком досок"""
    return render_template('boards.html')

@web_bp.route('/boards/<int:board_id>')
def board_detail(board_id):
    """Страница конкретной доски"""
    return render_template('board_detail.html', board_id=board_id)

@web_bp.route('/teams')
def teams_list():
    """Страница со списком команд"""
    return render_template('teams.html')

@web_bp.route('/teams/<int:team_id>')
def team_detail(team_id):
    """Страница конкретной команды"""
    return render_template('team_detail.html', team_id=team_id)