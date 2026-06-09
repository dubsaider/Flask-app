const TasksPage = {
    allTasks: [],

    async init() {
        TaskFilters.hideAssigneeFilter(true);
        TaskFilters.showMineOption(false);
        TaskFilters.bind(() => this.applyFilters());
        document.getElementById('tasks-group-by')?.addEventListener('change', () => this.applyFilters());

        try {
            this.allTasks = await API.getUserTasks(Auth.getCurrentUser().id);
            this.applyFilters();
        } catch (error) {
            console.error('Error loading tasks:', error);
            this.showEmpty('⚠️', 'Не удалось загрузить задачи');
        }
    },

    applyFilters() {
        const filters = TaskFilters.read();
        const userId = Auth.getCurrentUser().id;
        const filtered = TaskFilters.filterCards(this.allTasks, filters, userId);
        const groupBy = document.getElementById('tasks-group-by')?.value || 'board';

        TaskFilters.updateCount(filtered.length, this.allTasks.length);
        this.render(filtered, groupBy);
    },

    render(tasks, groupBy) {
        const container = document.getElementById('tasks-content');
        if (!container) return;

        DOM.clear(container);

        if (!tasks.length) {
            this.showEmpty('📭', 'Нет задач по выбранным фильтрам');
            return;
        }

        if (groupBy === 'none') {
            const group = this.buildGroup('Все задачи', tasks);
            container.appendChild(group);
            return;
        }

        const groups = this.groupTasks(tasks, groupBy);
        groups.forEach(({ title, items }) => {
            container.appendChild(this.buildGroup(title, items));
        });
    },

    groupTasks(tasks, groupBy) {
        const map = new Map();

        tasks.forEach(task => {
            let key;
            if (groupBy === 'board') {
                key = task.board_title;
            } else if (groupBy === 'priority') {
                key = PRIORITY_LABELS[task.priority] || task.priority;
            } else if (groupBy === 'status') {
                key = TaskWorkflow.label(task);
            }
            if (!map.has(key)) map.set(key, []);
            map.get(key).push(task);
        });

        return Array.from(map.entries()).map(([title, items]) => ({ title, items }));
    },

    buildGroup(title, tasks) {
        const groupNode = DOM.clone('tpl-task-group');
        DOM.setField(groupNode, 'title', title);
        DOM.setField(groupNode, 'count', String(tasks.length));

        const list = groupNode.querySelector('[data-field="list"]');
        tasks.forEach(task => list.appendChild(this.buildTaskRow(task)));

        return groupNode;
    },

    buildTaskRow(task) {
        const row = DOM.clone('tpl-task-row');
        const link = row.querySelector('[data-field="link"]');
        const stripe = row.querySelector('[data-field="stripe"]');
        const priority = task.priority || 'medium';

        link.href = `/board/${task.board_id}`;
        stripe.classList.add(`task-row__stripe--${priority}`);
        DOM.setField(row, 'title', task.title);

        const statusLabel = TaskWorkflow.label(task);
        const overdue = TaskFilters.isOverdue(task.deadline) && TaskWorkflow.status(task) === 'active'
            ? ' · просрочена' : '';
        DOM.setField(row, 'meta',
            `${task.board_title} · ${task.column_title} · ${PRIORITY_LABELS[priority]} · ${statusLabel}${overdue}`
        );

        return row;
    },

    showEmpty(icon, text) {
        const container = document.getElementById('tasks-content');
        if (!container) return;
        DOM.clear(container);
        const node = DOM.clone('tpl-empty-state');
        DOM.setField(node, 'icon', icon);
        DOM.setField(node, 'text', text);
        container.appendChild(node);
    }
};
