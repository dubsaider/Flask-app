/**
 * Права доступа на основе объекта permissions из API.
 * Контекст задаётся через setContext() после загрузки команды.
 */
const Permissions = {
    _permissions: {},
    _roleSlug: 'none',
    _roleName: '',

    setContext(permissions, roleSlug, roleName) {
        this._permissions = permissions || {};
        this._roleSlug = roleSlug || 'none';
        this._roleName = roleName || '';
    },

    getRoleSlug() {
        return this._roleSlug;
    },

    getRoleName() {
        return this._roleName;
    },

    getRole(team) {
        return Auth.getUserContext(team).slug;
    },

    has(key) {
        return !!this._permissions[key];
    },

    canViewBoard() {
        return this.has('view_board');
    },

    canComment() {
        return this.has('comment');
    },

    canCreateCard() {
        return this.has('create_card');
    },

    canEditCard() {
        return this.has('edit_card');
    },

    canDeleteCard() {
        return this.has('delete_card');
    },

    canMoveCard(card, userId) {
        if (this.has('move_card')) return true;
        if (this.has('move_card_own_only') && card?.assignee_id === userId) return true;
        return false;
    },

    canMoveAnyCard() {
        return this.has('move_card');
    },

    canMoveOwnCard() {
        return this.has('move_card_own_only');
    },

    canManageColumns() {
        return this.has('manage_columns');
    },

    canManageBoard() {
        return this.has('manage_board');
    },

    canAssign() {
        return this.has('assign_card');
    },

    canArchive() {
        return this.has('archive_card');
    },

    canManageTeamMembers() {
        return this.has('manage_team_members');
    },

    canManageRoles() {
        return this.has('manage_roles');
    },

    canViewDashboard() {
        return this.has('view_dashboard');
    },

    canViewAllTasks() {
        return this.has('view_all_tasks');
    },

    isReadOnlyCard() {
        return !this.canEditCard();
    },

    getRoleLabel(roleOrName) {
        if (typeof roleOrName === 'string' && ROLE_LABELS[roleOrName]) {
            return ROLE_LABELS[roleOrName];
        }
        return this._roleName || ROLE_LABELS[roleOrName] || roleOrName || '';
    },

    getRoleDescription(role) {
        if (role && ROLE_DESCRIPTIONS[role]) {
            return ROLE_DESCRIPTIONS[role];
        }
        return '';
    }
};
