const Modals = {
    openCard(cardId = null, columnId = null) {
        const panel = document.getElementById('card-panel');
        if (!panel) return;

        if (!cardId && !Permissions.canCreateCard()) {
            return;
        }

        if (cardId) {
            Cards.loadCardForEdit(cardId);
        } else {
            this.prepareNewCard(columnId);
        }

        RichText.clearComment();

        const commentForm = document.querySelector('#card-panel .comment-form');
        if (commentForm) {
            commentForm.classList.toggle('hidden', !Permissions.canComment());
        }

        panel.classList.add('active');
        panel.setAttribute('aria-hidden', 'false');
        panel.querySelector('.card-panel__body')?.scrollTo(0, 0);
    },

    closeCard() {
        const panel = document.getElementById('card-panel');
        panel?.classList.remove('active');
        panel?.setAttribute('aria-hidden', 'true');
    },

    prepareNewCard(columnId) {
        document.getElementById('card-panel-title').textContent = 'Новая карточка';
        document.getElementById('card-panel-title')?.classList.add('hidden');
        const titleInput = document.getElementById('card-title-input');
        titleInput?.classList.remove('hidden');
        titleInput.value = '';
        document.getElementById('card-id').value = '';
        document.getElementById('card-column-id').value = columnId;
        document.getElementById('card-title-input').value = '';
        document.getElementById('card-readonly-hint')?.classList.add('hidden');
        document.getElementById('card-panel')?.classList.remove('card-panel--readonly');
        document.getElementById('card-panel-meta')?.replaceChildren();
        document.getElementById('card-panel-chips')?.replaceChildren();
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
            const hasAssignee = el.querySelector('#card-assignee-input');
            const hasArchive = el.querySelector('#card-archived-input');
            if (hasAssignee) {
                el.classList.toggle('hidden', !Permissions.canAssign());
            } else if (hasArchive) {
                el.classList.toggle('hidden', !Permissions.canArchive());
            } else {
                el.classList.toggle('hidden', !Permissions.canManageBoard());
            }
        });

        Cards.populateAssigneeSelect(null);
        RichText.clearCard();
        titleInput?.focus();
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
    document.getElementById('card-panel-close')?.addEventListener('click', () => Modals.closeCard());
    document.getElementById('card-cancel-btn')?.addEventListener('click', () => Modals.closeCard());

    document.getElementById('board-modal-close')?.addEventListener('click', () => Modals.closeBoard());
    document.getElementById('board-cancel-btn')?.addEventListener('click', () => Modals.closeBoard());

    document.getElementById('column-modal-close')?.addEventListener('click', () => Modals.closeColumn());
    document.getElementById('column-cancel-btn')?.addEventListener('click', () => Modals.closeColumn());
    document.getElementById('column-delete-btn')?.addEventListener('click', () => Columns.deleteColumn());

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && document.getElementById('card-panel')?.classList.contains('active')) {
            Modals.closeCard();
        }
    });

    document.addEventListener('click', (event) => {
        if (event.target.classList.contains('modal')) {
            event.target.classList.remove('active');
        }
    });
});
