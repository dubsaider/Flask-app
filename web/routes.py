from flask import render_template, redirect, url_for
from .init import web_bp

@web_bp.route('/')
def index():
    return redirect(url_for('web.login'))

@web_bp.route('/login')
def login():
    return render_template('login.html')

@web_bp.route('/board/<int:board_id>')
def board_page(board_id):
    return render_template('board.html', board_id=board_id)

@web_bp.route('/tasks')
def tasks_page():
    return render_template('tasks.html')

@web_bp.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')

@web_bp.route('/team/<int:team_id>/settings')
def team_settings_page(team_id):
    return render_template('team_settings.html', team_id=team_id)
