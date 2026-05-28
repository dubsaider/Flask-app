from flask import Blueprint

# Создаем Blueprint для API
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Импортируем все модули API
from . import users
from . import teams
from . import boards
from . import columns
from . import cards