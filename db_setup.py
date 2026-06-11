"""Проверка и восстановление схемы БД при старте."""
from pathlib import Path

from flask_migrate import upgrade
from sqlalchemy import inspect, text

from extensions import db


def ensure_database(app) -> None:
    """Применить миграции; восстановить схему, если alembic_version есть, а таблиц нет."""
    migrations_dir = Path(app.root_path) / 'migrations'
    if not app.config.get('AUTO_MIGRATE', True):
        return

    with app.app_context():
        if migrations_dir.exists():
            upgrade()
        else:
            db.create_all()
            return

        if _has_core_tables():
            return

        # alembic помечен как head, но таблицы отсутствуют (битая/очищенная БД)
        inspector = inspect(db.engine)
        if 'alembic_version' in inspector.get_table_names():
            with db.engine.begin() as conn:
                conn.execute(text('DELETE FROM alembic_version'))

        upgrade()

        if not _has_core_tables():
            db.create_all()


def _has_core_tables() -> bool:
    inspector = inspect(db.engine)
    tables = set(inspector.get_table_names())
    required = {'users', 'teams', 'boards', 'cards', 'notifications'}
    return required.issubset(tables)
