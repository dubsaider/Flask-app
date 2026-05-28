from flask import Blueprint

# Создаем Blueprint для веб-страниц
web_bp = Blueprint('web', __name__)

# Импортируем маршруты
from . import routes