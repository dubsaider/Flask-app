const Sidebar = {
    workspace: [],
    currentBoardId: null,
    currentPage: 'board',
    collapsed: false,

    async init(boardId, pageName = 'board') {
        this.currentBoardId = boardId;
        this.currentPage = pageName;
        this.restoreCollapsedState();
        this.bindEvents();
        await this.loadWorkspace();
        this.updateNav();
        this.updateUserInfo();
        Notifications.init();
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
            btn.setAttribute('aria-label', this.collapsed
                ? Locale.get('nav.expand_sidebar')
                : Locale.get('nav.collapse_sidebar'));
            btn.title = this.collapsed
                ? Locale.get('nav.expand_sidebar')
                : Locale.get('nav.collapse_sidebar');
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

    updateNav() {
        const showDashboard = this.workspace.some(group => group.permissions?.view_dashboard);
        const teamWithSettings = this.workspace.find(group =>
            group.permissions?.manage_roles || group.permissions?.manage_team_members
        );
        const showTeamSettings = Boolean(teamWithSettings);

        document.getElementById('nav-dashboard')?.classList.toggle('hidden', !showDashboard);

        const settingsLink = document.getElementById('nav-team-settings');
        settingsLink?.classList.toggle('hidden', !showTeamSettings);
        if (settingsLink && teamWithSettings) {
            settingsLink.href = `/team/${teamWithSettings.team.id}/settings`;
        }

        document.querySelectorAll('.sidebar-page-link').forEach(link => {
            const active = link.dataset.page === this.currentPage;
            link.classList.toggle('is-active', active);
            if (active) {
                link.setAttribute('aria-current', 'page');
            } else {
                link.removeAttribute('aria-current');
            }
        });
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

    updateRole(roleKey, roleName) {
        const roleEl = document.getElementById('sidebar-user-role');
        if (!roleEl) return;

        roleEl.textContent = roleName || Permissions.getRoleLabel(roleKey);
        roleEl.title = Permissions.getRoleDescription(roleKey);
    },

    refresh(boardId) {
        this.currentBoardId = boardId;
        this.renderBoardList();
    }
};
