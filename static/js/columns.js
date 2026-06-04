const Columns = {
    async add() {
        const title = prompt('Column title:');
        if (!title || !Board.boardId) return;

        try {
            await API.createColumn(Board.boardId, { title });
            Board.loadColumns();
        } catch (error) {
            alert('Error creating column: ' + error.message);
        }
    },

    async saveColumn(event) {
        event.preventDefault();

        const columnId = parseInt(document.getElementById('column-id').value);
        const title = document.getElementById('column-title-input').value;

        try {
            await API.updateColumn(columnId, { title });
            Modals.closeColumn();
            Board.loadColumns();
        } catch (error) {
            alert('Error updating column: ' + error.message);
        }
    },

    async deleteColumn() {
        const columnId = document.getElementById('column-id').value;
        if (!columnId || !confirm('Delete this column and all its cards?')) return;

        try {
            await API.deleteColumn(parseInt(columnId));
            Modals.closeColumn();
            Board.loadColumns();
        } catch (error) {
            alert('Error deleting column: ' + error.message);
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('column-form')?.addEventListener('submit', (e) => Columns.saveColumn(e));
});
