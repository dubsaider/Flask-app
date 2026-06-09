const Modals = {
    openCard(cardId = null, columnId = null) {
        const modal = document.getElementById('card-modal');
        if (!modal) return;

        const role = Permissions.getRole(window.currentTeam);

        if (!cardId && !Permissions.canCreateCard(role)) {
            return;
        }

        if (cardId) {
            Cards.loadCardForEdit(cardId);
        } else {
            this.prepareNewCard(columnId, role);
        }

        const commentForm = document.querySelector('#card-modal .comment-form');
        if (commentForm) {
            commentForm.classList.toggle('hidden', !Permissions.canComment(role));
        }

        modal.classList.add('active');
    },

    closeCard() {
        document.getElementById('card-modal')?.classList.remove('active');
    },

    prepareNewCard(columnId, role) {
        document.getElementById('card-modal-title').textContent = 'Новая карточка';
        document.getElementById('card-id').value = '';
        document.getElementById('card-column-id').value = columnId;
        document.getElementById('card-title-input').value = '';
        document.getElementById('card-description-input').value = '';
        document.getElementById('card-priority-input').value = 'medium';
        document.getElementById('card-deadline-input').value = '';
        const archivedInput = document.getElementById('card-archived-input');
        if (archivedInput) archivedInput.checked = false;
        DOM.show(document.getElementById('card-form'));
        DOM.hide(document.getElementById('card-view-only'));
        document.getElementById('comments-list')?.replaceChildren();

        document.querySelector('#card-form .card-edit-actions')?.classList.remove('hidden');
        document.getElementById('card-delete-btn')?.classList.add('hidden');
        document.querySelectorAll('#card-form .leader-only').forEach(el => {
            el.classList.toggle('hidden', !Permissions.canManageBoard(role));
        });

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

    openColumn(columnId, currentTitle, isDone = false) {
        document.getElementById('column-id').value = columnId;
        document.getElementById('column-title-input').value = currentTitle;
        document.getElementById('column-modal-title').textContent = currentTitle;
        const isDoneInput = document.getElementById('column-is-done-input');
        if (isDoneInput) isDoneInput.checked = !!isDone;
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
