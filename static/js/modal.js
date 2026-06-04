const Modals = {
    openCard(cardId = null, columnId = null) {
        const modal = document.getElementById('card-modal');
        if (!modal) return;

        const userRole = Auth.getUserRole(window.currentTeam);

        document.querySelectorAll('.curator-only').forEach(el => {
            el.classList.toggle('hidden', userRole !== 'curator');
        });

        document.querySelectorAll('.member-only').forEach(el => {
            el.classList.toggle('hidden', !['leader', 'developer'].includes(userRole));
        });

        document.querySelectorAll('.leader-only').forEach(el => {
            el.classList.toggle('hidden', userRole !== 'leader');
        });

        if (cardId) {
            Cards.loadCardForEdit(cardId);
        } else {
            this.prepareNewCard(columnId);
        }

        modal.classList.add('active');
    },

    closeCard() {
        document.getElementById('card-modal')?.classList.remove('active');
    },

    prepareNewCard(columnId) {
        document.getElementById('card-modal-title').textContent = 'Новая карточка';
        document.getElementById('card-id').value = '';
        document.getElementById('card-column-id').value = columnId;
        document.getElementById('card-title-input').value = '';
        document.getElementById('card-description-input').value = '';
        document.getElementById('card-priority-input').value = 'medium';
        document.getElementById('card-status-input').value = 'active';
        document.getElementById('card-deadline-input').value = '';
        DOM.show(document.getElementById('card-form'));
        DOM.hide(document.getElementById('card-view-only'));
        document.getElementById('comments-list')?.replaceChildren();
        Cards.populateAssigneeSelect(null);
    },

    openBoard() {
        const board = window.currentBoard;
        if (board) {
            document.getElementById('board-title-input').value = board.title;
            document.getElementById('board-description-input').value = board.description || '';
        }
        document.getElementById('board-modal')?.classList.add('active');
    },

    closeBoard() {
        document.getElementById('board-modal')?.classList.remove('active');
    },

    openColumn(columnId, currentTitle) {
        document.getElementById('column-id').value = columnId;
        document.getElementById('column-title-input').value = currentTitle;
        document.getElementById('column-modal-title').textContent = currentTitle;
        document.getElementById('column-modal')?.classList.add('active');
    },

    closeColumn() {
        document.getElementById('column-modal')?.classList.remove('active');
    }
};

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('card-modal-close')?.addEventListener('click', () => Modals.closeCard());
    document.getElementById('card-cancel-btn')?.addEventListener('click', () => Modals.closeCard());

    document.getElementById('board-modal-close')?.addEventListener('click', () => Modals.closeBoard());
    document.getElementById('board-cancel-btn')?.addEventListener('click', () => Modals.closeBoard());

    document.getElementById('column-modal-close')?.addEventListener('click', () => Modals.closeColumn());
    document.getElementById('column-cancel-btn')?.addEventListener('click', () => Modals.closeColumn());
    document.getElementById('column-delete-btn')?.addEventListener('click', () => Columns.deleteColumn());

    document.addEventListener('click', (event) => {
        if (event.target.classList.contains('modal')) {
            event.target.classList.remove('active');
        }
    });
});
