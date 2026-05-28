from flask import Flask
from database import init_db
from api.init import api_bp
from web.init import web_bp

def create_app():
    """Создание и настройка приложения"""
    app = Flask(__name__)
    
    # Регистрируем blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(web_bp)
    
    # Инициализация базы данных
    with app.app_context():
        init_db()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)