from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

from . import users
from . import teams
from . import boards
from . import columns
from . import cards
from . import comments
from . import tasks
from . import notifications