const DragDrop = {
    instances: [],

    destroy() {
        this.instances.forEach(instance => {
            try {
                instance.destroy();
            } catch (e) {
                /* уже уничтожен */
            }
        });
        this.instances = [];
    },

    init(columns) {
        this.destroy();

        if (!Permissions.canMoveAnyCard() && !Permissions.canMoveOwnCard()) return;

        const userId = Auth.getCurrentUser().id;

        columns.forEach(column => {
            const cardsList = document.getElementById(`cards-${column.id}`);
            if (!cardsList) return;

            const sortable = new Sortable(cardsList, {
                group: 'kanban-cards',
                animation: 150,
                ghostClass: 'dragging',
                draggable: '.card-item--draggable',
                emptyInsertThreshold: 8,
                onEnd: (evt) => this.handleDrop(evt, userId)
            });

            this.instances.push(sortable);
        });

        if (Permissions.canManageColumns()) {
            this.initColumnReorder();
        }
    },

    initColumnReorder() {
        const container = document.getElementById('board-container');
        if (!container) return;

        const sortable = new Sortable(container, {
            animation: 150,
            draggable: '.column',
            handle: '.column-drag-handle',
            filter: '.add-column-btn',
            ghostClass: 'column-dragging',
            onEnd: (evt) => Columns.handleReorder(evt)
        });

        this.instances.push(sortable);
    },

    handleDrop(evt, userId) {
        const cardId = parseInt(evt.item.dataset.cardId, 10);
        const newColumnEl = evt.to.closest('.column');
        const oldColumnEl = evt.from.closest('.column');

        if (!newColumnEl || !cardId) {
            Board.loadColumns();
            return;
        }

        const newColumnId = parseInt(newColumnEl.dataset.columnId, 10);
        const oldColumnId = parseInt(oldColumnEl?.dataset.columnId, 10);

        if (evt.oldIndex === evt.newIndex && newColumnId === oldColumnId) {
            return;
        }

        API.moveCard(cardId, {
            column_id: newColumnId,
            position: evt.newIndex,
            user_id: userId
        }).catch(() => Board.loadColumns());
    }
};
