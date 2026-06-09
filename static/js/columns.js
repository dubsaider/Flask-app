const Columns = {
    async add() {
        const title = prompt('Название колонки:');
        if (!title || !Board.boardId) return;

        try {
            await API.createColumn(Board.boardId, {
                title,
                user_id: Auth.getCurrentUser().id
            });
            Board.loadColumns();
        } catch (error) {
            alert('Ошибка создания колонки: ' + error.message);
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
            alert('Ошибка изменения порядка колонок: ' + error.message);
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
            alert('Ошибка сохранения колонки: ' + error.message);
        }
    },

    async deleteColumn() {
        const columnId = document.getElementById('column-id').value;
        if (!columnId || !confirm('Удалить колонку и все карточки в ней?')) return;

        try {
            await API.deleteColumn(parseInt(columnId), { user_id: Auth.getCurrentUser().id });
            Modals.closeColumn();
            Board.loadColumns();
        } catch (error) {
            alert('Ошибка удаления колонки: ' + error.message);
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('column-form')?.addEventListener('submit', (e) => Columns.saveColumn(e));
});
