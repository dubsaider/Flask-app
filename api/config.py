from flask import jsonify
from .init import api_bp
from config import client_config, get_config


@api_bp.route('/config', methods=['GET'])
def get_app_config():
    """Публичные настройки для клиента."""
    return jsonify(client_config(get_config()))
