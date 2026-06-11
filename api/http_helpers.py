"""Общие HTTP-ответы API."""
from flask import jsonify


def forbidden(message='Access denied'):
    return jsonify({'error': message}), 403


def not_found(message='Not found'):
    return jsonify({'error': message}), 404


def bad_request(message):
    return jsonify({'error': message}), 400


def access_denied(error):
    """error — кортеж (message, status_code) из permissions.check_access."""
    if not error:
        return None
    return jsonify({'error': error[0]}), error[1]
