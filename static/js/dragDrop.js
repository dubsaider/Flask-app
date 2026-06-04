const DragDrop = {
    init(columns, role) {
        const userId = Auth.getCurrentUser().id;

        columns.forEach(column => {
            const cardsList = document.getElementById(`cards-${column.id}`);
            if (!cardsList) return;

            const hasDraggable = cardsList.querySelector('.card-item--draggable');
            if (!hasDraggable) return;

            new Sortable(cardsList, {
                group: 'shared',
                animation: 150,
                ghostClass: 'dragging',
                draggable: '.card-item--draggable',
                onEnd: (evt) => this.handleDrop(evt, userId)
            });
        });
    },

    handleDrop(evt, userId) {
        const cardId = parseInt(evt.item.dataset.cardId);
        const newColumnEl = evt.to.closest('.column');

        if (!newColumnEl || !cardId) {
            Board.loadColumns();
            return;
        }

        API.moveCard(cardId, {
            column_id: parseInt(newColumnEl.dataset.columnId),
            position: evt.newIndex,
            user_id: userId
        }).catch(() => Board.loadColumns());
    }
};
