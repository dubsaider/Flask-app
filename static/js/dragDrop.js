// Drag & Drop функциональность
const DragDrop = {
    init(columns) {
        columns.forEach(column => {
            const cardsList = document.getElementById(`cards-${column.id}`);
            if (!cardsList) return;
            
            new Sortable(cardsList, {
                group: 'shared',
                animation: 150,
                ghostClass: 'dragging',
                onEnd: (evt) => this.handleDrop(evt)
            });
        });
    },
    
    handleDrop(evt) {
        const cardId = parseInt(evt.item.dataset.cardId);
        const newColumnEl = evt.to.closest('.column');
        
        if (!newColumnEl || !cardId) {
            Board.loadColumns();
            return;
        }
        
        const newColumnId = parseInt(newColumnEl.dataset.columnId);
        const newPosition = evt.newIndex;
        
        API.moveCard(cardId, {
            column_id: newColumnId,
            position: newPosition
        }).catch(() => Board.loadColumns());
    }
};
