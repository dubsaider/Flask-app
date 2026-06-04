const DashboardPage = {
    async init() {
        const role = await this.resolveAccess();
        if (!role) return;

        try {
            const data = await API.getLeaderDashboard(Auth.getCurrentUser().id);
            this.render(data);
        } catch (error) {
            console.error('Error loading dashboard:', error);
            this.showEmpty('⚠️', 'Не удалось загрузить дашборд');
        }
    },

    async resolveAccess() {
        const workspace = await API.getUserWorkspace(Auth.getCurrentUser().id);
        const isLeader = workspace.some(group => group.role === 'leader');

        if (!isLeader) {
            this.showEmpty('🔒', 'Дашборд доступен только руководителям команд');
            return false;
        }
        return true;
    },

    render(teams) {
        const container = document.getElementById('dashboard-content');
        if (!container) return;

        DOM.clear(container);

        teams.forEach(teamData => {
            container.appendChild(this.buildTeamSection(teamData));
        });
    },

    buildTeamSection(data) {
        const section = DOM.clone('tpl-dashboard-team');
        DOM.setField(section, 'team-name', data.team.name);

        const boardNames = data.boards.map(b => b.title).join(', ') || 'Нет досок';
        DOM.setField(section, 'boards', boardNames);

        const statsContainer = section.querySelector('[data-field="stats"]');
        this.buildSummaryStats(data.summary).forEach(stat => statsContainer.appendChild(stat));

        this.buildAssigneeList(section, data.by_assignee, data.summary.active);
        this.buildPriorityList(section, data.by_priority);
        this.buildIssuesList(section, data.overdue_tasks, data.unassigned_tasks);

        return section;
    },

    buildSummaryStats(summary) {
        return [
            { value: summary.total, label: 'Всего задач' },
            { value: summary.active, label: 'Активных' },
            { value: summary.completed, label: 'Завершено' },
            { value: summary.overdue, label: 'Просрочено' },
            { value: summary.unassigned, label: 'Без исполнителя' }
        ].map(item => {
            const node = DOM.clone('tpl-stat-card');
            DOM.setField(node, 'value', String(item.value));
            DOM.setField(node, 'label', item.label);
            return node;
        });
    },

    buildAssigneeList(section, assignees, maxActive) {
        const container = section.querySelector('[data-field="assignee-list"]');
        DOM.clear(container);

        if (!assignees.length) {
            container.appendChild(this.makePanelEmpty('Нет назначенных задач'));
            return;
        }

        const max = Math.max(...assignees.map(a => a.active), 1);
        assignees.forEach(item => {
            const row = DOM.clone('tpl-assignee-bar');
            DOM.setField(row, 'name', item.username);
            DOM.setField(row, 'count', `${item.active} акт. / ${item.overdue} проср.`);

            const fill = row.querySelector('[data-field="fill"]');
            fill.style.width = `${Math.round((item.active / max) * 100)}%`;

            container.appendChild(row);
        });
    },

    buildPriorityList(section, byPriority) {
        const container = section.querySelector('[data-field="priority-list"]');
        DOM.clear(container);

        const total = Object.values(byPriority).reduce((a, b) => a + b, 0) || 1;

        Object.entries(byPriority).forEach(([key, count]) => {
            const row = DOM.clone('tpl-priority-row');
            DOM.setField(row, 'label', PRIORITY_LABELS[key] || key);
            DOM.setField(row, 'count', String(count));

            const bar = row.querySelector('[data-field="bar"]');
            bar.classList.add(`priority-row__bar--${key}`);
            bar.style.width = `${Math.round((count / total) * 100)}%`;

            container.appendChild(row);
        });
    },

    buildIssuesList(section, overdue, unassigned) {
        const container = section.querySelector('[data-field="issues-list"]');
        DOM.clear(container);

        const issues = [
            ...overdue.map(task => ({ task, type: 'overdue' })),
            ...unassigned.map(task => ({ task, type: 'unassigned' }))
        ];

        if (!issues.length) {
            container.appendChild(this.makePanelEmpty('Нет проблемных задач'));
            return;
        }

        issues.forEach(({ task, type }) => {
            const row = DOM.clone('tpl-issue-row');
            const link = row.querySelector('[data-field="link"]');
            link.href = `/board/${task.board_id}`;

            DOM.setField(row, 'title', task.title);
            const prefix = type === 'overdue' ? '⚠ Просрочена' : '○ Без исполнителя';
            DOM.setField(row, 'meta',
                `${prefix} · ${task.board_title} · ${task.column_title}`
            );

            container.appendChild(row);
        });
    },

    makePanelEmpty(text) {
        const node = DOM.clone('tpl-empty-state');
        DOM.setField(node, 'icon', '');
        DOM.setField(node, 'text', text);
        return node;
    },

    showEmpty(icon, text) {
        const container = document.getElementById('dashboard-content');
        if (!container) return;
        DOM.clear(container);
        const node = DOM.clone('tpl-empty-state');
        DOM.setField(node, 'icon', icon);
        DOM.setField(node, 'text', text);
        container.appendChild(node);
    }
};
