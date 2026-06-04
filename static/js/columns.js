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

    async saveColumn(event) {
        event.preventDefault();

        const columnId = parseInt(document.getElementById('column-id').value);
        const title = document.getElementById('column-title-input').value;

        try {
            await API.updateColumn(columnId, {
                title,
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
