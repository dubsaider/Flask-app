"""Фикстуры для интеграционных тестов API."""
import pytest

from app import create_app
from extensions import db
from models.seed import seed_demo_data


# Демо-данные из models/seed.py
LEADER_ID = 3       # charlie — руководитель team 1
DEVELOPER_ID = 1    # alice — разработчик team 1
TEAM_ID = 1
COLUMN_TODO = 1
COLUMN_IN_PROGRESS = 2


@pytest.fixture
def app():
    application = create_app('testing')
    application.config.update({
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'AUTO_MIGRATE': False,
        'TESTING': True,
    })

    with application.app_context():
        db.drop_all()
        db.create_all()
        with db.engine.begin() as conn:
            seed_demo_data(conn)

    yield application

    with application.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
