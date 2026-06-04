const Cards = {
    async loadCardForEdit(cardId) {
        const card = await API.getCard(cardId);
        const userRole = Auth.getUserRole(window.currentTeam);

        document.getElementById('card-modal-title').textContent = card.title;
        document.getElementById('card-id').value = card.id;
        document.getElementById('card-column-id').value = card.column_id;
        document.getElementById('card-title-input').value = card.title;
        document.getElementById('card-description-input').value = card.description || '';
        document.getElementById('card-priority-input').value = card.priority || 'medium';
        document.getElementById('card-status-input').value = card.status || 'active';
        document.getElementById('card-deadline-input').value = card.deadline
            ? card.deadline.replace(' ', 'T').slice(0, 16)
            : '';

        this.populateAssigneeSelect(card.assignee_id);

        const cardForm = document.getElementById('card-form');
        const viewOnly = document.getElementById('card-view-only');

        if (userRole === 'curator') {
            DOM.hide(cardForm);
            DOM.show(viewOnly);
            document.getElementById('view-title').textContent = card.title;
            document.getElementById('view-description').textContent = card.description || '—';

            const priorityEl = document.getElementById('view-priority');
            const priority = card.priority || 'medium';
            priorityEl.textContent = PRIORITY_LABELS[priority] || priority;
            priorityEl.className = `view-priority-badge view-priority-badge--${priority}`;
        } else {
            DOM.show(cardForm);
            DOM.hide(viewOnly);
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
        const userRole = Auth.getUserRole(window.currentTeam);
        const currentUser = Auth.getCurrentUser();

        const data = {
            title: document.getElementById('card-title-input').value,
            description: document.getElementById('card-description-input').value,
            priority: document.getElementById('card-priority-input').value,
            status: document.getElementById('card-status-input').value,
            deadline: document.getElementById('card-deadline-input').value || null,
            user_id: currentUser.id
        };

        const assigneeSelect = document.getElementById('card-assignee-input');
        if (assigneeSelect && userRole === 'leader') {
            data.assignee_id = assigneeSelect.value ? parseInt(assigneeSelect.value) : null;
        }

        try {
            if (cardId) {
                await API.updateCard(parseInt(cardId), data);
            } else {
                data.column_id = columnId;
                if (userRole === 'leader') {
                    data.created_by = currentUser.id;
                }
                await API.createCard(data);
            }

            Modals.closeCard();
            Board.loadColumns();
        } catch (error) {
            alert('Ошибка сохранения: ' + error.message);
        }
    },

    async deleteCard() {
        const cardId = document.getElementById('card-id').value;
        if (!cardId || !confirm('Удалить эту карточку?')) return;

        try {
            await API.deleteCard(parseInt(cardId));
            Modals.closeCard();
            Board.loadColumns();
        } catch (error) {
            alert('Ошибка удаления: ' + error.message);
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('card-form')?.addEventListener('submit', (e) => Cards.saveCard(e));
    document.getElementById('card-delete-btn')?.addEventListener('click', () => Cards.deleteCard());
});
