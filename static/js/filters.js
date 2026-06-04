const TaskFilters = {
    read() {
        return {
            search: document.getElementById('filter-search')?.value.trim().toLowerCase() || '',
            priority: document.getElementById('filter-priority')?.value || '',
            status: document.getElementById('filter-status')?.value || '',
            assignee: document.getElementById('filter-assignee')?.value || '',
            overdue: document.getElementById('filter-overdue')?.checked || false,
            mine: document.getElementById('filter-mine')?.checked || false
        };
    },

    isOverdue(deadline) {
        if (!deadline) return false;
        const date = new Date(deadline.replace(' ', 'T'));
        return !Number.isNaN(date.getTime()) && date < new Date();
    },

    matches(card, filters, userId) {
        if (filters.search) {
            const text = `${card.title} ${card.description || ''}`.toLowerCase();
            if (!text.includes(filters.search)) return false;
        }
        if (filters.priority && card.priority !== filters.priority) return false;
        if (filters.status && card.status !== filters.status) return false;
        if (filters.assignee === 'unassigned' && card.assignee_id) return false;
        if (filters.assignee && filters.assignee !== 'unassigned' &&
            String(card.assignee_id) !== filters.assignee) return false;
        if (filters.overdue && !this.isOverdue(card.deadline)) return false;
        if (filters.mine && card.assignee_id !== userId) return false;
        return true;
    },

    filterCards(cards, filters, userId) {
        return (cards || []).filter(card => this.matches(card, filters, userId));
    },

    filterColumns(columns, filters, userId) {
        return columns.map(column => ({
            ...column,
            cards: this.filterCards(column.cards, filters, userId)
        }));
    },

    countCards(columns) {
        return columns.reduce((sum, col) => sum + (col.cards?.length || 0), 0);
    },

    populateAssignees(members) {
        const select = document.getElementById('filter-assignee');
        if (!select) return;

        while (select.options.length > 2) {
            select.remove(2);
        }

        (members || []).forEach(member => {
            const option = document.createElement('option');
            option.value = member.id;
            option.textContent = member.username;
            select.appendChild(option);
        });
    },

    showMineOption(show) {
        document.getElementById('filter-mine-wrap')?.classList.toggle('hidden', !show);
    },

    hideAssigneeFilter(hide) {
        document.querySelector('.filter-group--assignee')?.classList.toggle('hidden', hide);
    },

    bind(onChange) {
        ['filter-search', 'filter-priority', 'filter-status', 'filter-assignee',
            'filter-overdue', 'filter-mine'].forEach(id => {
            const el = document.getElementById(id);
            el?.addEventListener('input', onChange);
            el?.addEventListener('change', onChange);
        });

        document.getElementById('filter-reset')?.addEventListener('click', () => {
            const search = document.getElementById('filter-search');
            if (search) search.value = '';
            const priority = document.getElementById('filter-priority');
            if (priority) priority.value = '';
            const status = document.getElementById('filter-status');
            if (status) status.value = '';
            const assignee = document.getElementById('filter-assignee');
            if (assignee) assignee.value = '';
            const overdue = document.getElementById('filter-overdue');
            if (overdue) overdue.checked = false;
            const mine = document.getElementById('filter-mine');
            if (mine) mine.checked = false;
            onChange();
        });
    },

    updateCount(shown, total) {
        const el = document.getElementById('filter-result-count');
        if (!el) return;
        el.textContent = shown === total
            ? `Показано: ${total}`
            : `Показано: ${shown} из ${total}`;
    }
};
