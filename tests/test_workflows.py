"""Сквозные сценарии работы с задачами и ролями."""
from tests.conftest import (
    COLUMN_IN_PROGRESS,
    COLUMN_TODO,
    DEVELOPER_ID,
    LEADER_ID,
    TEAM_ID,
)


def test_create_task(client):
    """Руководитель создаёт задачу в колонке «To Do»."""
    response = client.post('/api/cards', json={
        'user_id': LEADER_ID,
        'column_id': COLUMN_TODO,
        'title': 'Интеграционная задача',
        'description': '<p>Описание тестовой задачи</p>',
        'priority': 'high',
    })

    assert response.status_code == 201
    data = response.get_json()
    assert data['title'] == 'Интеграционная задача'
    assert data['column_id'] == COLUMN_TODO
    assert data['priority'] == 'high'
    assert data['created_by'] == LEADER_ID


def test_move_task_between_columns(client):
    """Задача переносится из одной колонки в другую."""
    create = client.post('/api/cards', json={
        'user_id': LEADER_ID,
        'column_id': COLUMN_TODO,
        'title': 'Задача для переноса',
        'assignee_id': DEVELOPER_ID,
        'priority': 'medium',
    })
    assert create.status_code == 201
    card_id = create.get_json()['id']

    columns_before = client.get(f'/api/boards/1/columns')
    assert columns_before.status_code == 200
    todo_before = next(c for c in columns_before.get_json() if c['id'] == COLUMN_TODO)
    progress_before = next(c for c in columns_before.get_json() if c['id'] == COLUMN_IN_PROGRESS)
    assert any(c['id'] == card_id for c in todo_before['cards'])
    assert not any(c['id'] == card_id for c in progress_before['cards'])

    move = client.put(f'/api/cards/{card_id}/move', json={
        'user_id': DEVELOPER_ID,
        'column_id': COLUMN_IN_PROGRESS,
        'position': 0,
    })
    assert move.status_code == 200
    assert move.get_json()['message'] == 'Card moved successfully'

    columns_after = client.get(f'/api/boards/1/columns')
    assert columns_after.status_code == 200
    todo_after = next(c for c in columns_after.get_json() if c['id'] == COLUMN_TODO)
    progress_after = next(c for c in columns_after.get_json() if c['id'] == COLUMN_IN_PROGRESS)
    assert not any(c['id'] == card_id for c in todo_after['cards'])
    assert any(c['id'] == card_id for c in progress_after['cards'])

    card = client.get(f'/api/cards/{card_id}')
    assert card.status_code == 200
    assert card.get_json()['column_id'] == COLUMN_IN_PROGRESS


def test_create_custom_role(client):
    """Руководитель создаёт новую роль на основе шаблона developer."""
    roles_before = client.get(
        f'/api/teams/{TEAM_ID}/roles',
        query_string={'user_id': LEADER_ID},
    )
    assert roles_before.status_code == 200
    count_before = len(roles_before.get_json())

    response = client.post(f'/api/teams/{TEAM_ID}/roles', json={
        'user_id': LEADER_ID,
        'template_key': 'developer',
        'name': 'QA Engineer',
        'description': 'Тестирование и проверка задач',
    })

    assert response.status_code == 201
    role = response.get_json()
    assert role['name'] == 'QA Engineer'
    assert role['description'] == 'Тестирование и проверка задач'
    assert role['template_key'] == 'developer'
    assert role['is_system'] is False
    assert role['permissions']['view_board'] is True
    assert role['permissions']['comment'] is True
    assert role['permissions']['move_card_own_only'] is True
    assert role['permissions']['edit_card'] is False

    roles_after = client.get(
        f'/api/teams/{TEAM_ID}/roles',
        query_string={'user_id': LEADER_ID},
    )
    assert roles_after.status_code == 200
    assert len(roles_after.get_json()) == count_before + 1
    assert any(r['name'] == 'QA Engineer' for r in roles_after.get_json())


def test_create_task_forbidden_for_developer_without_permission(client):
    """Разработчик не может создавать задачи (только руководитель)."""
    response = client.post('/api/cards', json={
        'user_id': DEVELOPER_ID,
        'column_id': COLUMN_TODO,
        'title': 'Не должна создаться',
    })
    assert response.status_code == 403
