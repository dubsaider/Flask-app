const Columns = {
    async add() {
        const title = prompt(Locale.get('column.name_prompt'));
        if (!title || !Board.boardId) return;

        try {
            await API.createColumn(Board.boardId, {
                title,
                user_id: Auth.getCurrentUser().id
            });
            Board.loadColumns();
        } catch (error) {
            alert(`${Locale.get('column.create_error')}: ${error.message}`);
        }
    },

    async handleReorder(evt) {
        if (evt.oldIndex === evt.newIndex) return;

        const container = document.getElementById('board-container');
        if (!container) return;

        const columnIds = [...container.querySelectorAll('.column')]
            .map(el => parseInt(el.dataset.columnId, 10))
            .filter(id => !Number.isNaN(id));

        try {
            await API.reorderColumns(Board.boardId, {
                user_id: Auth.getCurrentUser().id,
                column_ids: columnIds
            });
            await Board.loadColumns();
        } catch (error) {
            alert(`${Locale.get('column.reorder_error')}: ${error.message}`);
            Board.loadColumns();
        }
    },

    async saveColumn(event) {
        event.preventDefault();

        const columnId = parseInt(document.getElementById('column-id').value);
        const title = document.getElementById('column-title-input').value;
        const isDone = document.getElementById('column-is-done-input')?.checked || false;

        try {
            await API.updateColumn(columnId, {
                title,
                is_done: isDone,
                user_id: Auth.getCurrentUser().id
            });
            Modals.closeColumn();
            Board.loadColumns();
        } catch (error) {
            alert(`${Locale.get('column.save_error')}: ${error.message}`);
        }
    },

    async deleteColumn() {
        const columnId = document.getElementById('column-id').value;
        if (!columnId || !confirm(Locale.get('column.delete_confirm'))) return;

        try {
            await API.deleteColumn(parseInt(columnId), { user_id: Auth.getCurrentUser().id });
            Modals.closeColumn();
            Board.loadColumns();
        } catch (error) {
            alert(`${Locale.get('column.delete_error')}: ${error.message}`);
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('column-form')?.addEventListener('submit', (e) => Columns.saveColumn(e));
});
