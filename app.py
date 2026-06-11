from flask import Flask
from config import client_config, get_config
from database import init_db, init_app as init_db_app
from api.init import api_bp
from web.init import web_bp


def create_app(config_name=None):
    """Создание и настройка приложения."""
    app = Flask(__name__)

    config_class = get_config(config_name)
    app.config.from_object(config_class)

    init_db_app(app)

    app.register_blueprint(api_bp)
    app.register_blueprint(web_bp)

    @app.context_processor
    def inject_client_config():
        return {'client_config': client_config(app.config)}

    with app.app_context():
        init_db()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(
        debug=app.config['DEBUG'],
        host=app.config['HOST'],
        port=app.config['PORT'],
    )
