const Sidebar = {
    workspace: [],
    currentBoardId: null,
    collapsed: false,

    async init(boardId) {
        this.currentBoardId = boardId;
        this.restoreCollapsedState();
        this.bindEvents();
        await this.loadWorkspace();
        this.updateUserInfo();
    },

    bindEvents() {
        document.getElementById('sidebar-collapse-btn')?.addEventListener('click', () => {
            this.toggleCollapsed();
        });

        document.getElementById('sidebar-logout-btn')?.addEventListener('click', () => Auth.logout());
    },

    restoreCollapsedState() {
        this.collapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        this.applyCollapsedState();
    },

    toggleCollapsed() {
        this.collapsed = !this.collapsed;
        localStorage.setItem('sidebarCollapsed', String(this.collapsed));
        this.applyCollapsedState();
    },

    applyCollapsedState() {
        const sidebar = document.getElementById('sidebar');
        const btn = document.getElementById('sidebar-collapse-btn');
        if (!sidebar) return;

        sidebar.classList.toggle('sidebar--collapsed', this.collapsed);

        if (btn) {
            btn.setAttribute('aria-expanded', String(!this.collapsed));
            btn.setAttribute('aria-label', this.collapsed ? 'Развернуть панель' : 'Свернуть панель');
            btn.title = this.collapsed ? 'Развернуть панель' : 'Свернуть панель';
        }
    },

    async loadWorkspace() {
        const user = Auth.getCurrentUser();
        if (!user) return;

        try {
            this.workspace = await API.getUserWorkspace(user.id);
            this.renderBoardList();
        } catch (error) {
            console.error('Error loading workspace:', error);
        }
    },

    renderBoardList() {
        const container = document.getElementById('sidebar-board-groups');
        if (!container) return;

        DOM.clear(container);

        this.workspace.forEach(group => {
            const groupNode = DOM.clone('tpl-sidebar-team');
            DOM.setField(groupNode, 'team-name', group.team.name);

            const list = groupNode.querySelector('[data-field="board-list"]');

            group.boards.forEach(board => {
                const boardNode = DOM.clone('tpl-sidebar-board');
                const link = boardNode.querySelector('[data-field="link"]');
                const shortLabel = board.title.charAt(0).toUpperCase();

                DOM.setField(boardNode, 'title', board.title);
                DOM.setField(boardNode, 'short', shortLabel);
                link.href = `/board/${board.id}`;
                link.title = `${group.team.name}: ${board.title}`;

                if (board.id === this.currentBoardId) {
                    link.classList.add('is-active');
                    link.setAttribute('aria-current', 'page');
                }

                list.appendChild(boardNode);
            });

            container.appendChild(groupNode);
        });
    },

    updateUserInfo() {
        const user = Auth.getCurrentUser();
        if (!user) return;

        const avatar = document.getElementById('sidebar-user-avatar');
        const name = document.getElementById('sidebar-user-name');
        const role = document.getElementById('sidebar-user-role');

        if (avatar) {
            avatar.textContent = user.username.charAt(0).toUpperCase();
            avatar.title = user.username;
        }
        if (name) name.textContent = user.username;
        if (role) role.textContent = '';
    },

    updateRole(roleKey) {
        const roleEl = document.getElementById('sidebar-user-role');
        if (!roleEl) return;

        roleEl.textContent = Permissions.getRoleLabel(roleKey);
        roleEl.title = Permissions.getRoleDescription(roleKey);
    },

    refresh(boardId) {
        this.currentBoardId = boardId;
        this.renderBoardList();
    }
};
