from dotenv import load_dotenv
from flask import Flask

from config import client_config, get_config
from labels import get_labels
from db_setup import ensure_database
from extensions import db, migrate
from api.init import api_bp
from web.init import web_bp

# Импорт моделей для Alembic autogenerate
import models.schema  # noqa: F401


def create_app(config_name=None):
    """Создание и настройка приложения."""
    load_dotenv()

    app = Flask(__name__)

    config_class = get_config(config_name)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(api_bp)
    app.register_blueprint(web_bp)

    @app.context_processor
    def inject_globals():
        return {
            'client_config': client_config(app.config),
            'labels': get_labels(),
        }

    with app.app_context():
        ensure_database(app)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(
        debug=app.config['DEBUG'],
        host=app.config['HOST'],
        port=app.config['PORT'],
    )
