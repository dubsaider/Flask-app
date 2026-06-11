"""Единый источник UI-текстов (шаблоны + фронтенд)."""

APP_NAME = 'Kanban Board'
BRAND_NAME = 'Kanban'

PRIORITY_LABELS = {
    'low': 'Низкий',
    'medium': 'Средний',
    'high': 'Высокий',
    'critical': 'Критический',
}

WORKFLOW_LABELS = {
    'active': 'В работе',
    'completed': 'Завершена',
    'archived': 'В архиве',
}

ROLE_LABELS = {
    'leader': 'Руководитель',
    'developer': 'Разработчик',
    'curator': 'Куратор',
    'none': 'Нет доступа',
}

ROLE_DESCRIPTIONS = {
    'leader': 'Полное управление доской, задачами и командой',
    'developer': 'Перемещение своих задач на доске и комментарии',
    'curator': 'Просмотр и комментарии без редактирования',
    'none': '',
}

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
    'view_all_tasks': 'Просмотр всех задач',
}

LABELS = {
    'app': {
        'name': APP_NAME,
        'brand_short': 'KB',
        'brand_name': BRAND_NAME,
    },
    'common': {
        'all': 'Все',
        'save': 'Сохранить',
        'cancel': 'Отмена',
        'delete': 'Удалить',
        'close': 'Закрыть',
        'loading': 'Загрузка...',
        'login': 'Войти',
        'logout': 'Выйти',
        'guest': 'Guest',
        'unassigned': 'Не назначен',
        'reset': 'Сбросить',
        'add': 'Добавить',
        'edit': 'Изменить',
        'submit': 'Отправить',
        'error': 'Ошибка',
        'not_set': 'Не задан',
    },
    'nav': {
        'boards': 'Доски',
        'my_tasks': 'Мои задачи',
        'dashboard': 'Дашборд',
        'team': 'Команда',
        'notifications': 'Уведомления',
        'read_all': 'Прочитать все',
        'collapse_sidebar': 'Свернуть панель',
        'expand_sidebar': 'Развернуть панель',
    },
    'auth': {
        'login_title': f'Вход — {APP_NAME}',
        'login_subtitle': 'Выберите пользователя для входа',
        'login_loading': 'Загрузка пользователей...',
        'login_error': 'Не удалось загрузить пользователей',
    },
    'board': {
        'title': f'Доска — {APP_NAME}',
        'loading': 'Загрузка...',
        'filters': 'Фильтры',
        'add_column': '+ Колонка',
        'add_card': '+ Добавить карточку',
        'add_column_btn': '+ Добавить колонку',
        'edit_board': 'Изменить',
        'delete_board': 'Удалить',
        'column_settings': 'Настройки колонки',
        'drag_column': 'Перетащить колонку',
        'access_denied_title': 'Доступ запрещён',
        'access_denied_message': 'Вы не являетесь участником этой команды',
        'delete_confirm': 'Удалить эту доску?',
        'save_error': 'Ошибка сохранения доски',
    },
    'card': {
        'panel_label': 'Карточка',
        'new_title': 'Новая карточка',
        'title_placeholder': 'Название задачи',
        'readonly_hint': (
            'Описание и параметры задачи редактирует только '
            '<strong>руководитель</strong>. Вы можете перемещать свои задачи '
            'на доске и оставлять комментарии.'
        ),
        'meta_assignee': 'Исполнитель',
        'meta_deadline': 'Дедлайн',
        'section_params': 'Параметры',
        'section_description': 'Описание',
        'assignee': 'Исполнитель',
        'priority': 'Приоритет',
        'deadline': 'Дедлайн',
        'archive': 'Архив',
        'archived_check': 'В архиве',
        'delete_confirm': 'Удалить эту карточку?',
        'save_error': 'Ошибка сохранения',
        'delete_error': 'Ошибка удаления',
        'no_create_permission': 'У вас нет прав на создание задач',
    },
    'column': {
        'title': 'Колонка',
        'name_label': 'Название',
        'name_prompt': 'Название колонки:',
        'drag_hint': 'Перетаскивайте заголовок колонки на доске, чтобы изменить порядок.',
        'is_done': 'Колонка завершения (Done) — задачи здесь считаются выполненными',
        'create_error': 'Ошибка создания колонки',
        'save_error': 'Ошибка сохранения колонки',
        'delete_confirm': 'Удалить колонку и все карточки в ней?',
        'delete_error': 'Ошибка удаления колонки',
        'reorder_error': 'Ошибка изменения порядка колонок',
    },
    'board_modal': {
        'title': 'Редактирование доски',
        'name': 'Название',
        'description': 'Описание',
        'name_placeholder': 'Sprint 1',
        'description_placeholder': 'Цели и контекст спринта',
    },
    'comments': {
        'title': 'Комментарии',
        'editor_placeholder': 'Написать комментарий...',
    },
    'filters': {
        'search': 'Поиск',
        'search_placeholder': 'Название или описание...',
        'priority': 'Приоритет',
        'status': 'Статус',
        'assignee': 'Исполнитель',
        'overdue_only': 'Только просроченные',
        'mine_only': 'Только мои задачи',
        'shown_all': 'Показано: {total}',
        'shown_partial': 'Показано: {shown} из {total}',
    },
    'tasks': {
        'page_title': f'Мои задачи — {APP_NAME}',
        'title': 'Мои задачи',
        'subtitle': 'Все назначенные вам задачи по проектам',
        'loading': 'Загрузка задач...',
        'load_error': 'Не удалось загрузить задачи',
        'empty': 'Нет задач по выбранным фильтрам',
        'all_tasks': 'Все задачи',
        'overdue_suffix': ' · просрочена',
        'group_by': 'Группировка:',
        'group_board': 'По доскам',
        'group_none': 'Список',
        'group_priority': 'По приоритету',
        'group_status': 'По статусу',
    },
    'dashboard': {
        'page_title': f'Дашборд — {APP_NAME}',
        'title': 'Дашборд руководителя',
        'subtitle': 'Обзор нагрузки и статуса задач по командам',
        'loading': 'Загрузка...',
        'load_error': 'Не удалось загрузить дашборд',
        'access_denied': 'Дашборд недоступен для вашей роли',
        'no_boards': 'Нет досок',
        'stat_total': 'Всего задач',
        'stat_active': 'Активных',
        'stat_completed': 'Завершено',
        'stat_overdue': 'Просрочено',
        'stat_unassigned': 'Без исполнителя',
        'panel_assignees': 'Нагрузка по исполнителям',
        'panel_priority': 'По приоритету',
        'panel_issues': 'Требуют внимания',
        'no_assignees': 'Нет назначенных задач',
        'no_issues': 'Нет проблемных задач',
        'assignee_count': '{active} акт. / {overdue} проср.',
        'issue_overdue': '⚠ Просрочена',
        'issue_unassigned': '○ Без исполнителя',
    },
    'team_settings': {
        'page_title': f'Настройки команды — Kanban',
        'title': 'Настройки команды',
        'default_desc': 'Управление ролями и участниками команды',
        'tab_roles': 'Роли',
        'tab_members': 'Участники',
        'create_from_template': 'Создать на основе шаблона',
        'create_role': 'Создать роль',
        'add_member': 'Добавить участника',
        'curator': 'Куратор команды',
        'role_desc_placeholder': 'Описание роли',
        'badge_template': 'Шаблон',
        'badge_custom': 'Своя роль',
        'template_basis': ' · основа: ',
        'change_role': 'Сменить роль',
        'role_saved': 'Роль сохранена',
        'delete_role_confirm': 'Удалить роль «{name}»?',
        'remove_member_confirm': 'Удалить {name} из команды?',
        'access_denied_title': 'Нет доступа',
        'access_denied_message': (
            'Настройки команды доступны пользователям с правом '
            'управления ролями или участниками.'
        ),
        'load_error': 'Не удалось загрузить настройки команды',
    },
    'notifications': {
        'empty': 'Нет уведомлений',
        'time_now': 'только что',
        'time_minutes': '{n} мин. назад',
        'time_hours': '{n} ч. назад',
    },
    'rich_text': {
        'card_placeholder': 'Подробности, ссылки, чек-лист...',
        'image_too_large': 'Изображение должно быть не больше 500 КБ',
    },
    'enums': {
        'priority': PRIORITY_LABELS,
        'workflow': WORKFLOW_LABELS,
        'roles': ROLE_LABELS,
        'role_descriptions': ROLE_DESCRIPTIONS,
        'permissions': PERMISSION_LABELS,
    },
}


def get_labels():
    return LABELS


def get_client_labels():
    """Словарь для передачи во фронтенд (window.APP_CONFIG.labels)."""
    return LABELS
