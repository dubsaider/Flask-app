const Board = {
    boardId: null,
    currentBoard: null,
    currentTeam: null,

    init(boardId) {
        this.boardId = boardId;
        this.bindActions();
        this.load();
    },

    bindActions() {
        document.getElementById('edit-board-btn')?.addEventListener('click', () => Modals.openBoard());
        document.getElementById('delete-board-btn')?.addEventListener('click', () => this.deleteBoard());

        document.getElementById('board-form')?.addEventListener('submit', async (event) => {
            event.preventDefault();
            try {
                await API.updateBoard(this.boardId, {
                    title: document.getElementById('board-title-input').value,
                    description: document.getElementById('board-description-input').value,
                    user_id: Auth.getCurrentUser().id
                });
                Modals.closeBoard();
                this.load();
            } catch (error) {
                alert('Ошибка сохранения доски: ' + error.message);
            }
        });
    },

    async load() {
        this.hideState();
        DOM.show(document.getElementById('board-container'));

        try {
            this.currentBoard = await API.getBoard(this.boardId);
            document.getElementById('board-title').textContent = this.currentBoard.title;
            document.getElementById('board-description').textContent = this.currentBoard.description || '';

            this.currentTeam = await API.getTeam(this.currentBoard.team_id);
            window.currentTeam = this.currentTeam;
            window.currentBoard = this.currentBoard;

            Sidebar.refresh(this.boardId);

            const role = Permissions.getRole(this.currentTeam);
            Sidebar.updateRole(role);

            if (!Permissions.canViewBoard(role)) {
                this.showState('🔒', 'Доступ запрещён', 'Вы не являетесь участником этой команды', [
                    { text: 'Войти', href: '/login', primary: true }
                ]);
                return;
            }

            this.applyPermissions(role);
            this.showRoleInfo(role);
            await this.loadColumns();
        } catch (error) {
            console.error('Error loading board:', error);
            this.showState('⚠️', 'Ошибка', error.message, []);
        }
    },

    showState(icon, title, message, actions) {
        DOM.hide(document.getElementById('board-container'));

        const state = document.getElementById('board-state');
        document.getElementById('board-state-icon').textContent = icon;
        document.getElementById('board-state-title').textContent = title;
        document.getElementById('board-state-message').textContent = message;

        const actionsContainer = document.getElementById('board-state-actions');
        DOM.clear(actionsContainer);

        actions.forEach(action => {
            const node = DOM.clone('tpl-state-action');
            const link = node.querySelector('[data-field="action-link"]');
            link.textContent = action.text;
            link.href = action.href;
            link.classList.add('btn');
            if (!action.primary) link.classList.add('btn-secondary');
            actionsContainer.appendChild(node);
        });

        DOM.show(state);
    },

    hideState() {
        DOM.hide(document.getElementById('board-state'));
    },

    applyPermissions(role) {
        document.querySelectorAll('.board-actions.leader-only').forEach(el => {
            el.classList.toggle('hidden', !Permissions.canManageBoard(role));
        });
    },

    showRoleInfo(role) {
        const container = document.getElementById('role-info');
        const descEl = document.getElementById('role-description');
        if (!container) return;

        const icons = {
            leader: '👑',
            developer: '👨‍💻',
            curator: '👁️'
        };

        DOM.clear(container);
        const badge = DOM.clone('tpl-role-badge');
        const badgeEl = badge.querySelector('[data-field="badge"]');
        badgeEl.textContent = `${icons[role] || ''} ${Permissions.getRoleLabel(role)}`.trim();
        badgeEl.classList.add(`role-badge--${role}`);
        container.appendChild(badge);
        DOM.show(container);

        if (descEl) {
            descEl.textContent = Permissions.getRoleDescription(role);
            DOM.show(descEl);
        }
    },

    async loadColumns() {
        const columns = await API.getColumns(this.boardId);
        const role = Permissions.getRole(this.currentTeam);
        this.render(columns, role);

        if (role === 'leader' || role === 'developer') {
            DragDrop.init(columns, role);
        }
    },

    render(columns, role) {
        const container = document.getElementById('board-container');
        if (!container) return;

        const userId = Auth.getCurrentUser().id;
        DOM.clear(container);

        columns.forEach(column => {
            const columnNode = DOM.clone('tpl-board-column');
            const columnEl = columnNode.querySelector('[data-field="column"]');
            const titleBtn = columnNode.querySelector('[data-field="title-btn"]');
            const menuBtn = columnNode.querySelector('[data-field="menu-btn"]');
            const cardsList = columnNode.querySelector('[data-field="cards-list"]');
            const addCardBtn = columnNode.querySelector('[data-field="add-card-btn"]');

            columnEl.dataset.columnId = column.id;
            cardsList.id = `cards-${column.id}`;
            titleBtn.textContent = column.title;

            if (Permissions.canManageColumns(role)) {
                DOM.show(menuBtn);
                const openColumn = () => Modals.openColumn(column.id, column.title);
                titleBtn.addEventListener('click', openColumn);
                menuBtn.addEventListener('click', openColumn);
            } else {
                titleBtn.disabled = true;
            }

            (column.cards || []).forEach(card => {
                cardsList.appendChild(this.createCardElement(card, role, userId));
            });

            if (Permissions.canCreateCard(role)) {
                DOM.show(addCardBtn);
                addCardBtn.addEventListener('click', () => Modals.openCard(null, column.id));
            }

            container.appendChild(columnNode);
        });

        if (Permissions.canManageColumns(role)) {
            const addColumnNode = DOM.clone('tpl-add-column-btn');
            addColumnNode.querySelector('[data-field="add-column-btn"]')
                .addEventListener('click', () => Columns.add());
            container.appendChild(addColumnNode);
        }
    },

    createCardElement(card, role, userId) {
        const node = DOM.clone('tpl-card-item');
        const cardEl = node.querySelector('[data-field="card"]');
        const priority = card.priority || 'medium';

        cardEl.dataset.cardId = card.id;
        DOM.setField(node, 'title', card.title);

        const stripe = node.querySelector('[data-field="priority-stripe"]');
        stripe.classList.add(`card-item__stripe--${priority}`);

        const priorityChip = node.querySelector('[data-field="priority"]');
        priorityChip.classList.add(`card-chip--${priority}`);
        DOM.setField(node, 'priority-text', PRIORITY_LABELS[priority] || priority);

        if (card.assignee) {
            const assignee = node.querySelector('[data-field="assignee"]');
            assignee.textContent = card.assignee.username.charAt(0).toUpperCase();
            assignee.title = card.assignee.username;
            DOM.show(assignee);
        }

        if (card.deadline) {
            DOM.show(node.querySelector('[data-field="deadline"]'));
        }

        if (card.comments?.length) {
            DOM.setField(node, 'comments-count', String(card.comments.length));
            DOM.show(node.querySelector('[data-field="comments"]'));
        }

        if (Permissions.canMoveCard(role, card, userId)) {
            cardEl.classList.add('card-item--draggable');
        }

        cardEl.addEventListener('click', () => Modals.openCard(card.id));
        return node;
    },

    async deleteBoard() {
        if (!confirm('Удалить эту доску?')) return;

        await API.deleteBoard(this.boardId, { user_id: Auth.getCurrentUser().id });
        await Auth.redirectToDefaultBoard();
    }
};
