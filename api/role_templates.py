"""Шаблоны ролей и описание прав доступа."""
import json

from labels import PERMISSION_LABELS, ROLE_DESCRIPTIONS, ROLE_LABELS

ALL_PERMISSION_KEYS = list(PERMISSION_LABELS.keys())


def _all_permissions(enabled=True):
    return {key: enabled for key in ALL_PERMISSION_KEYS}


def _permissions(**enabled):
    base = _all_permissions(False)
    base.update(enabled)
    return base


ROLE_TEMPLATES = {
    'leader': {
        'name': ROLE_LABELS['leader'],
        'description': ROLE_DESCRIPTIONS['leader'],
        'permissions': _all_permissions(True),
        'is_system': True,
    },
    'developer': {
        'name': ROLE_LABELS['developer'],
        'description': ROLE_DESCRIPTIONS['developer'],
        'permissions': _permissions(view_board=True, comment=True, move_card_own_only=True),
        'is_system': True,
    },
    'curator': {
        'name': ROLE_LABELS['curator'],
        'description': ROLE_DESCRIPTIONS['curator'],
        'permissions': _permissions(view_board=True, comment=True),
        'is_system': True,
    },
}


def default_permissions():
    return _all_permissions(False)


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


def template_permissions_for_client():
    """Матрица прав шаблонов для window.APP_CONFIG."""
    return {
        key: normalize_permissions(template['permissions'])
        for key, template in ROLE_TEMPLATES.items()
    }
