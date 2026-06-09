/**
 * Ролевая модель (зеркало api/permissions.py)
 *
 * Куратор      — просмотр + комментарии
 * Руководитель — полное управление командой и доской
 * Разработчик  — перемещение своих задач и комментарии
 */
const Permissions = {
    getRole(team) {
        return Auth.getUserRole(team);
    },

    canViewBoard(role) {
        return ['curator', 'leader', 'developer'].includes(role);
    },

    canComment(role) {
        return this.canViewBoard(role);
    },

    canCreateCard(role) {
        return role === 'leader';
    },

    canEditCard(role) {
        return role === 'leader';
    },

    canDeleteCard(role) {
        return role === 'leader';
    },

    canMoveCard(role, card, userId) {
        if (role === 'leader') return true;
        if (role === 'developer') return card?.assignee_id === userId;
        return false;
    },

    canManageColumns(role) {
        return role === 'leader';
    },

    canManageBoard(role) {
        return role === 'leader';
    },

    canAssign(role) {
        return role === 'leader';
    },

    isReadOnlyCard(role) {
        return role !== 'leader';
    },

    getRoleLabel(role) {
        return ROLE_LABELS[role] || '';
    },

    getRoleDescription(role) {
        return ROLE_DESCRIPTIONS[role] || '';
    }
};
