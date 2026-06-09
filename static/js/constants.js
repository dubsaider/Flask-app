const PRIORITY_LABELS = {
    low: 'Низкий',
    medium: 'Средний',
    high: 'Высокий',
    critical: 'Критический'
};

const ROLE_LABELS = {
    leader: 'Руководитель',
    developer: 'Разработчик',
    curator: 'Куратор',
    none: 'Нет доступа'
};

const ROLE_DESCRIPTIONS = {
    leader: 'Полное управление доской, задачами и командой',
    developer: 'Перемещение своих задач на доске и комментарии',
    curator: 'Просмотр и комментарии без редактирования',
    none: ''
};

const TEMPLATE_PERMISSIONS = {
    leader: {
        view_board: true, comment: true, create_card: true, edit_card: true,
        delete_card: true, move_card: true, move_card_own_only: true,
        assign_card: true, archive_card: true, manage_columns: true,
        manage_board: true, manage_team_members: true, manage_roles: true,
        view_dashboard: true, view_all_tasks: true
    },
    developer: {
        view_board: true, comment: true, move_card_own_only: true
    },
    curator: {
        view_board: true, comment: true
    }
};

const PERMISSION_LABELS = {
    view_board: 'Просмотр доски',
    comment: 'Комментарии',
    create_card: 'Создание задач',
    edit_card: 'Редактирование задач',
    delete_card: 'Удаление задач',
    move_card: 'Перемещение любых задач',
    move_card_own_only: 'Перемещение своих задач',
    assign_card: 'Назначение исполнителя',
    archive_card: 'Архивирование задач',
    manage_columns: 'Управление колонками',
    manage_board: 'Управление досками',
    manage_team_members: 'Управление участниками',
    manage_roles: 'Настройка ролей',
    view_dashboard: 'Дашборд команды',
    view_all_tasks: 'Просмотр всех задач'
};

const WORKFLOW_LABELS = {
    active: 'В работе',
    completed: 'Завершена',
    archived: 'В архиве'
};

const TaskWorkflow = {
    status(card) {
        if (card.workflow_status) return card.workflow_status;
        if (card.status === 'archived') return 'archived';
        if (card.is_completed || card.column_is_done) return 'completed';
        return 'active';
    },

    label(card) {
        return WORKFLOW_LABELS[this.status(card)] || this.status(card);
    }
};
