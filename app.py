from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_migrate import upgrade

from config import client_config, get_config
from database import init_app as init_db_app
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
    init_db_app(app)

    app.register_blueprint(api_bp)
    app.register_blueprint(web_bp)

    @app.context_processor
    def inject_client_config():
        return {'client_config': client_config(app.config)}

    with app.app_context():
        migrations_dir = Path(app.root_path) / 'migrations'
        if app.config.get('AUTO_MIGRATE', True) and migrations_dir.exists():
            upgrade()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(
        debug=app.config['DEBUG'],
        host=app.config['HOST'],
        port=app.config['PORT'],
    )
