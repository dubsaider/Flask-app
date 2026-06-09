const Cards = {
    showReadOnlyView(card, ctx) {
        const panel = document.getElementById('card-panel');
        panel?.classList.add('card-panel--readonly');

        DOM.hide(document.getElementById('card-form'));
        DOM.show(document.getElementById('card-view-only'));

        document.getElementById('card-panel-title').textContent = card.title;
        document.getElementById('card-title-input')?.classList.add('hidden');
        document.getElementById('card-panel-title')?.classList.remove('hidden');

        RichText.renderHtml(document.getElementById('view-description'), card.description);
        this.renderHeaderMeta(card);
        this.renderMetaRow(card);

        const hint = document.getElementById('card-readonly-hint');
        if (hint) {
            hint.classList.toggle('hidden', Permissions.canEditCard() || !Permissions.canMoveOwnCard());
        }
    },

    showEditForm(card) {
        const panel = document.getElementById('card-panel');
        panel?.classList.remove('card-panel--readonly');

        DOM.show(document.getElementById('card-form'));
        DOM.hide(document.getElementById('card-view-only'));
        document.getElementById('card-readonly-hint')?.classList.add('hidden');

        document.getElementById('card-panel-title')?.classList.add('hidden');
        const titleInput = document.getElementById('card-title-input');
        titleInput?.classList.remove('hidden');
        titleInput.value = card.title;

        document.getElementById('card-id').value = card.id;
        document.getElementById('card-column-id').value = card.column_id;
        RichText.setCardContent(card.description || '');
        document.getElementById('card-priority-input').value = card.priority || 'medium';
        document.getElementById('card-deadline-input').value = card.deadline
            ? card.deadline.replace(' ', 'T').slice(0, 16)
            : '';

        const archivedInput = document.getElementById('card-archived-input');
        if (archivedInput) {
            archivedInput.checked = card.status === 'archived';
        }

        this.populateAssigneeSelect(card.assignee_id);
        this.renderHeaderMeta(card);

        const editActions = document.querySelector('#card-form .card-edit-actions');
        editActions?.classList.remove('hidden');

        document.getElementById('card-delete-btn')?.classList.toggle(
            'hidden',
            !Permissions.canDeleteCard()
        );

        document.querySelectorAll('#card-form .leader-only').forEach(el => {
            const assigneeField = el.querySelector('#card-assignee-input');
            const archiveField = el.querySelector('#card-archived-input');
            if (assigneeField) {
                el.classList.toggle('hidden', !Permissions.canAssign());
            } else if (archiveField) {
                el.classList.toggle('hidden', !Permissions.canArchive());
            } else {
                el.classList.toggle('hidden', !Permissions.canManageBoard());
            }
        });

        document.getElementById('card-panel-meta').replaceChildren();
    },

    renderHeaderMeta(card) {
        const chips = document.getElementById('card-panel-chips');
        if (!chips) return;

        DOM.clear(chips);

        const priority = card.priority || 'medium';
        const priorityChip = document.createElement('span');
        priorityChip.className = `card-panel__chip card-panel__chip--priority-${priority}`;
        priorityChip.textContent = PRIORITY_LABELS[priority] || priority;
        chips.appendChild(priorityChip);

        const workflow = TaskWorkflow.status(card);
        const workflowChip = document.createElement('span');
        workflowChip.className = `card-panel__chip card-panel__chip--workflow-${workflow}`;
        workflowChip.textContent = TaskWorkflow.label(card);
        chips.appendChild(workflowChip);
    },

    renderMetaRow(card) {
        const meta = document.getElementById('card-panel-meta');
        if (!meta) return;

        DOM.clear(meta);

        const assigneeName = card.assignee?.username || 'Не назначен';
        meta.appendChild(this.makeMetaItem('Исполнитель', assigneeName));

        const deadlineText = card.deadline
            ? new Date(card.deadline.replace(' ', 'T')).toLocaleString('ru-RU', {
                day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit'
            })
            : 'Не задан';
        meta.appendChild(this.makeMetaItem('Дедлайн', deadlineText));
    },

    makeMetaItem(label, value) {
        const item = document.createElement('div');
        item.className = 'card-panel__meta-item';
        item.innerHTML = `
            <span class="card-panel__meta-label">${label}</span>
            <span class="card-panel__meta-value">${value}</span>
        `;
        return item;
    },

    async loadCardForEdit(cardId) {
        const card = await API.getCard(cardId);
        const ctx = Auth.getUserContext(window.currentTeam);

        document.getElementById('card-panel-title').textContent = card.title;

        if (Permissions.isReadOnlyCard()) {
            this.showReadOnlyView(card, ctx);
        } else {
            this.showEditForm(card);
        }

        Comments.loadComments(cardId);
    },

    populateAssigneeSelect(selectedId) {
        const select = document.getElementById('card-assignee-input');
        if (!select || !window.currentTeam) return;

        select.replaceChildren();

        const empty = document.createElement('option');
        empty.value = '';
        empty.textContent = 'Не назначен';
        select.appendChild(empty);

        window.currentTeam.members.forEach(member => {
            const option = document.createElement('option');
            option.value = member.id;
            option.textContent = member.username;
            if (selectedId && member.id === selectedId) {
                option.selected = true;
            }
            select.appendChild(option);
        });
    },

    async saveCard(event) {
        event.preventDefault();

        const cardId = document.getElementById('card-id').value;
        const columnId = parseInt(document.getElementById('card-column-id').value);
        const currentUser = Auth.getCurrentUser();

        const data = {
            title: document.getElementById('card-title-input').value,
            description: RichText.getCardContent(),
            priority: document.getElementById('card-priority-input').value,
            deadline: document.getElementById('card-deadline-input').value || null,
            user_id: currentUser.id
        };

        if (Permissions.canAssign()) {
            const assigneeSelect = document.getElementById('card-assignee-input');
            data.assignee_id = assigneeSelect?.value ? parseInt(assigneeSelect.value) : null;
        }
        if (Permissions.canArchive()) {
            data.archived = document.getElementById('card-archived-input')?.checked || false;
        }

        try {
            if (cardId) {
                await API.updateCard(parseInt(cardId), data);
            } else {
                if (!Permissions.canCreateCard()) {
                    alert('У вас нет прав на создание задач');
                    return;
                }
                data.column_id = columnId;
                await API.createCard(data);
            }

            Modals.closeCard();
            Board.loadColumns();
            Notifications.refresh();
        } catch (error) {
            alert('Ошибка сохранения: ' + error.message);
        }
    },

    async deleteCard() {
        const cardId = document.getElementById('card-id').value;
        if (!cardId || !confirm('Удалить эту карточку?')) return;

        try {
            await API.deleteCard(parseInt(cardId), { user_id: Auth.getCurrentUser().id });
            Modals.closeCard();
            Board.loadColumns();
            Notifications.refresh();
        } catch (error) {
            alert('Ошибка удаления: ' + error.message);
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('card-form')?.addEventListener('submit', (e) => Cards.saveCard(e));
    document.getElementById('card-delete-btn')?.addEventListener('click', () => Cards.deleteCard());
});
