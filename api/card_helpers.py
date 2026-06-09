"""Вычисление workflow-статуса задачи по колонке и полю status."""


def normalize_status(status):
    if status == 'completed':
        return 'active'
    if status in ('active', 'archived'):
        return status
    return 'active'


def workflow_status(status, column_is_done=False):
    status = normalize_status(status)
    if status == 'archived':
        return 'archived'
    if column_is_done:
        return 'completed'
    return 'active'


def is_completed(status, column_is_done=False):
    return workflow_status(status, column_is_done) == 'completed'


def is_in_progress(status, column_is_done=False):
    return workflow_status(status, column_is_done) == 'active'


def workflow_fields(status, column_is_done=False):
    ws = workflow_status(status, column_is_done)
    return {
        'status': normalize_status(status),
        'workflow_status': ws,
        'is_completed': ws == 'completed',
    }
