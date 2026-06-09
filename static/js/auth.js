const Auth = {
    currentUser: null,
    allUsers: [],

    async init() {
        try {
            this.allUsers = await API.getUsers();
        } catch (error) {
            console.error('Error loading users:', error);
            this.allUsers = [];
        }

        const savedUserId = localStorage.getItem('currentUserId');
        const savedUsername = localStorage.getItem('currentUsername');

        if (savedUserId && savedUsername) {
            this.currentUser = {
                id: parseInt(savedUserId),
                username: savedUsername
            };
        } else {
            this.currentUser = null;
        }
    },

    async requireAuth() {
        await this.init();
        if (!this.isAuthenticated()) {
            window.location.href = '/login';
            return false;
        }
        return true;
    },

    async login(userId, username) {
        this.currentUser = { id: parseInt(userId), username };
        localStorage.setItem('currentUserId', userId);
        localStorage.setItem('currentUsername', username);
        await this.redirectToDefaultBoard();
    },

    async redirectToDefaultBoard() {
        const user = this.getCurrentUser();
        if (!user) {
            window.location.href = '/login';
            return;
        }

        try {
            const workspace = await API.getUserWorkspace(user.id);
            const firstBoard = workspace.flatMap(group => group.boards)[0];

            if (firstBoard) {
                window.location.href = `/board/${firstBoard.id}`;
            } else {
                window.location.href = '/login';
            }
        } catch (error) {
            console.error('Error resolving default board:', error);
            window.location.href = '/login';
        }
    },

    logout() {
        this.currentUser = null;
        localStorage.removeItem('currentUserId');
        localStorage.removeItem('currentUsername');
        window.location.href = '/login';
    },

    getCurrentUser() {
        return this.currentUser;
    },

    isAuthenticated() {
        return this.currentUser !== null;
    },

    getUserContext(team) {
        if (!this.currentUser || !team) {
            return { slug: 'none', name: '', role_id: null, permissions: {} };
        }

        if (team.curator_id === this.currentUser.id) {
            const curatorRole = team.roles?.find(r => r.template_key === 'curator' || r.slug === 'curator');
            if (curatorRole) {
                return {
                    slug: curatorRole.slug,
                    name: curatorRole.name,
                    role_id: curatorRole.id,
                    permissions: curatorRole.permissions || {},
                };
            }
            return {
                slug: 'curator',
                name: ROLE_LABELS.curator,
                role_id: null,
                permissions: TEMPLATE_PERMISSIONS?.curator || { view_board: true, comment: true },
            };
        }

        const member = team.members?.find(m => m.id === this.currentUser.id);
        if (member) {
            const role = team.roles?.find(r => r.id === member.role_id);
            return {
                slug: member.role || role?.slug || 'none',
                name: member.role_name || role?.name || '',
                role_id: member.role_id || role?.id || null,
                permissions: role?.permissions || {},
            };
        }

        return { slug: 'none', name: '', role_id: null, permissions: {} };
    },

    getUserRole(team) {
        return this.getUserContext(team).slug;
    }
};
