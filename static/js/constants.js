const PRIORITY_LABELS = window.APP_CONFIG?.labels?.enums?.priority || {
    low: 'Низкий',
    medium: 'Средний',
    high: 'Высокий',
    critical: 'Критический'
};

const ROLE_LABELS = window.APP_CONFIG?.labels?.enums?.roles || {
    leader: 'Руководитель',
    developer: 'Разработчик',
    curator: 'Куратор',
    none: 'Нет доступа'
};

const ROLE_DESCRIPTIONS = window.APP_CONFIG?.labels?.enums?.role_descriptions || {
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

const PERMISSION_LABELS = window.APP_CONFIG?.labels?.enums?.permissions || {};

const WORKFLOW_LABELS = window.APP_CONFIG?.labels?.enums?.workflow || {
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
