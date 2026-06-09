const Cards = {
    showReadOnlyView(card) {
        DOM.hide(document.getElementById('card-form'));
        DOM.show(document.getElementById('card-view-only'));

        document.getElementById('view-title').textContent = card.title;
        document.getElementById('view-description').textContent = card.description || '—';

        const priorityEl = document.getElementById('view-priority');
        const priority = card.priority || 'medium';
        priorityEl.textContent = PRIORITY_LABELS[priority] || priority;
        priorityEl.className = `view-priority-badge view-priority-badge--${priority}`;
    },

    showEditForm(card, role) {
        DOM.show(document.getElementById('card-form'));
        DOM.hide(document.getElementById('card-view-only'));

        document.getElementById('card-modal-title').textContent = card.title;
        document.getElementById('card-id').value = card.id;
        document.getElementById('card-column-id').value = card.column_id;
        document.getElementById('card-title-input').value = card.title;
        document.getElementById('card-description-input').value = card.description || '';
        document.getElementById('card-priority-input').value = card.priority || 'medium';
        document.getElementById('card-deadline-input').value = card.deadline
            ? card.deadline.replace(' ', 'T').slice(0, 16)
            : '';

        const archivedInput = document.getElementById('card-archived-input');
        if (archivedInput) {
            archivedInput.checked = card.status === 'archived';
        }

        this.populateAssigneeSelect(card.assignee_id);

        const editActions = document.querySelector('#card-form .card-edit-actions');
        if (editActions) {
            editActions.classList.toggle('hidden', false);
        }

        document.getElementById('card-delete-btn')?.classList.toggle(
            'hidden',
            !Permissions.canDeleteCard(role)
        );

        document.querySelectorAll('#card-form .leader-only').forEach(el => {
            el.classList.toggle('hidden', !Permissions.canManageBoard(role));
        });
    },

    async loadCardForEdit(cardId) {
        const card = await API.getCard(cardId);
        const role = Permissions.getRole(window.currentTeam);
        const userId = Auth.getCurrentUser().id;

        if (Permissions.isReadOnlyCard(role, card, userId)) {
            document.getElementById('card-modal-title').textContent = card.title;
            this.showReadOnlyView(card);
        } else {
            this.showEditForm(card, role);
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
        const role = Permissions.getRole(window.currentTeam);
        const currentUser = Auth.getCurrentUser();

        const data = {
            title: document.getElementById('card-title-input').value,
            description: document.getElementById('card-description-input').value,
            priority: document.getElementById('card-priority-input').value,
            deadline: document.getElementById('card-deadline-input').value || null,
            user_id: currentUser.id
        };

        if (Permissions.canManageBoard(role)) {
            const assigneeSelect = document.getElementById('card-assignee-input');
            data.assignee_id = assigneeSelect?.value ? parseInt(assigneeSelect.value) : null;
            data.archived = document.getElementById('card-archived-input')?.checked || false;
        }

        try {
            if (cardId) {
                await API.updateCard(parseInt(cardId), data);
            } else {
                if (!Permissions.canCreateCard(role)) {
                    alert('Только руководитель может создавать задачи');
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
