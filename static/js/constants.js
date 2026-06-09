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
    developer: 'Работа со своими назначенными задачами',
    curator: 'Просмотр и комментарии без редактирования',
    none: ''
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
