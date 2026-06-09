"""Шаблоны ролей и описание прав доступа."""
import json

PERMISSION_LABELS = {
    'view_board': 'Просмотр доски',
    'comment': 'Комментарии',
    'create_card': 'Создание задач',
    'edit_card': 'Редактирование задач',
    'delete_card': 'Удаление задач',
    'move_card': 'Перемещение любых задач',
    'move_card_own_only': 'Перемещение своих задач',
    'assign_card': 'Назначение исполнителя',
    'archive_card': 'Архивирование задач',
    'manage_columns': 'Управление колонками',
    'manage_board': 'Управление досками',
    'manage_team_members': 'Управление участниками',
    'manage_roles': 'Настройка ролей',
    'view_dashboard': 'Дашборд команды',
    'view_all_tasks': 'Просмотр всех задач (фильтры)',
}

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
