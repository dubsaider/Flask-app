"""Шаблоны ролей и описание прав доступа."""
import json

from labels import PERMISSION_LABELS

ALL_PERMISSION_KEYS = list(PERMISSION_LABELS.keys())

_FULL = {key: True for key in ALL_PERMISSION_KEYS}

ROLE_TEMPLATES = {
    'leader': {
        'name': 'Руководитель',
        'description': 'Полное управление доской, задачами и командой',
        'permissions': dict(_FULL),
        'is_system': True,
    },
    'developer': {
        'name': 'Разработчик',
        'description': 'Перемещение своих задач на доске и комментарии',
        'permissions': {
            'view_board': True,
            'comment': True,
            'move_card_own_only': True,
        },
        'is_system': True,
    },
    'curator': {
        'name': 'Куратор',
        'description': 'Просмотр и комментарии без редактирования',
        'permissions': {
            'view_board': True,
            'comment': True,
        },
        'is_system': True,
    },
}


def default_permissions():
    return {key: False for key in ALL_PERMISSION_KEYS}


def normalize_permissions(raw):
    base = default_permissions()
    if not raw:
        return base
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            return base
    for key in ALL_PERMISSION_KEYS:
        if key in raw:
            base[key] = bool(raw[key])
    return base


def permissions_from_template(template_key):
    template = ROLE_TEMPLATES.get(template_key)
    if not template:
        return default_permissions()
    return normalize_permissions(template['permissions'])


def serialize_permissions(permissions):
    return json.dumps(normalize_permissions(permissions), ensure_ascii=False)


def templates_for_api():
    result = []
    for key, template in ROLE_TEMPLATES.items():
        result.append({
            'key': key,
            'name': template['name'],
            'description': template['description'],
            'permissions': normalize_permissions(template['permissions']),
            'is_system': template.get('is_system', True),
        })
    return result
