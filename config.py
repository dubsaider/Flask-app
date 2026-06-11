"""Конфигурация приложения.

Переопределение через переменные окружения или файл .env (если используете flask run / export).

Пример:
    FLASK_CONFIG=development
    DATABASE_PATH=kanban.db
    SECRET_KEY=your-secret-key
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.lower() in ('1', 'true', 'yes', 'on')


def _env_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


class Config:
    """Базовые настройки."""

    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')

    DATABASE_PATH = os.environ.get('DATABASE_PATH', str(BASE_DIR / 'kanban.db'))
    SCHEMA_PATH = os.environ.get('SCHEMA_PATH', str(BASE_DIR / 'schema.sql'))

    DEBUG = _env_bool('FLASK_DEBUG', True)
    HOST = os.environ.get('FLASK_HOST', '127.0.0.1')
    PORT = _env_int('FLASK_PORT', 5000)

    # HTML / rich-text
    MAX_HTML_LENGTH = _env_int('MAX_HTML_LENGTH', 50000)
    MAX_IMAGE_DATA_URL_LENGTH = _env_int('MAX_IMAGE_DATA_URL_LENGTH', 700000)
    RICH_TEXT_MAX_IMAGE_SIZE = _env_int('RICH_TEXT_MAX_IMAGE_SIZE', 512000)


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    DATABASE_PATH = os.environ.get(
        'DATABASE_PATH',
        str(BASE_DIR / 'kanban_test.db'),
    )


CONFIG_MAP = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}


def get_config(name: str | None = None) -> type[Config]:
    """Вернуть класс конфигурации по имени окружения."""
    config_name = name or os.environ.get('FLASK_CONFIG', 'development')
    return CONFIG_MAP.get(config_name, DevelopmentConfig)


def _cfg_value(cfg, key, default=None):
    """Прочитать значение из Flask app.config (dict) или класса Config."""
    if hasattr(cfg, 'get') and callable(cfg.get):
        return cfg.get(key, default)
    return getattr(cfg, key, default)


def client_config(cfg=None) -> dict:
    """Настройки, безопасные для передачи в браузер."""
    if cfg is None:
        cfg = get_config()
    if isinstance(cfg, type):
        cfg = cfg()
    return {
        'richTextMaxImageSize': _cfg_value(cfg, 'RICH_TEXT_MAX_IMAGE_SIZE', 512000),
    }
