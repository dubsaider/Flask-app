// API запросы
const API = {
    async get(url) {
        const response = await fetch(url);
        if (!response.ok) throw new Error(await response.text());
        return response.json();
    },

    async post(url, data) {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error(await response.text());
        return response.json();
    },

    async put(url, data) {
        const response = await fetch(url, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error(await response.text());
        return response.json();
    },

    async delete(url, data) {
        const options = { method: 'DELETE' };
        if (data) {
            options.headers = { 'Content-Type': 'application/json' };
            options.body = JSON.stringify(data);
        }
        const response = await fetch(url, options);
        if (!response.ok) throw new Error(await response.text());
    },

    getUsers: () => API.get('/api/users'),
    getUserWorkspace: (userId) => API.get(`/api/users/${userId}/workspace`),
    getUserTasks: (userId) => API.get(`/api/users/${userId}/tasks`),
    getLeaderDashboard: (userId) => API.get(`/api/users/${userId}/leader-dashboard`),

    getNotifications: (userId) => API.get(`/api/users/${userId}/notifications?user_id=${userId}`),
    getUnreadNotificationCount: (userId) =>
        API.get(`/api/users/${userId}/notifications/unread-count?user_id=${userId}`),
    markNotificationRead: (id, userId) =>
        API.put(`/api/notifications/${id}/read`, { user_id: userId }),
    markAllNotificationsRead: (userId) =>
        API.put(`/api/users/${userId}/notifications/read-all`, { user_id: userId }),

    getTeam: (id) => API.get(`/api/teams/${id}`),
    updateTeam: (id, data) => API.put(`/api/teams/${id}`, data),

    getRoleTemplates: () => API.get('/api/role-templates'),
    getTeamRoles: (teamId, userId) => API.get(`/api/teams/${teamId}/roles?user_id=${userId}`),
    createTeamRole: (teamId, data) => API.post(`/api/teams/${teamId}/roles`, data),
    updateTeamRole: (teamId, roleId, data) => API.put(`/api/teams/${teamId}/roles/${roleId}`, data),
    deleteTeamRole: (teamId, roleId, data) => API.delete(`/api/teams/${teamId}/roles/${roleId}`, data),

    addTeamMember: (teamId, data) => API.post(`/api/teams/${teamId}/members`, data),
    removeTeamMember: (teamId, data) => API.delete(`/api/teams/${teamId}/members`, data),
    updateTeamMember: (teamId, memberUserId, data) =>
        API.put(`/api/teams/${teamId}/members/${memberUserId}`, data),

    getBoard: (id) => API.get(`/api/boards/${id}`),
    updateBoard: (id, data) => API.put(`/api/boards/${id}`, data),
    deleteBoard: (id, data) => API.delete(`/api/boards/${id}`, data),
    getColumns: (boardId) => API.get(`/api/boards/${boardId}/columns`),

    createColumn: (boardId, data) => API.post(`/api/boards/${boardId}/columns`, data),
    reorderColumns: (boardId, data) => API.put(`/api/boards/${boardId}/columns/reorder`, data),
    updateColumn: (id, data) => API.put(`/api/columns/${id}`, data),
    deleteColumn: (id, data) => API.delete(`/api/columns/${id}`, data),

    getCard: (id) => API.get(`/api/cards/${id}`),
    createCard: (data) => API.post('/api/cards', data),
    updateCard: (id, data) => API.put(`/api/cards/${id}`, data),
    deleteCard: (id, data) => API.delete(`/api/cards/${id}`, data),
    moveCard: (id, data) => API.put(`/api/cards/${id}/move`, data),

    getComments: (cardId) => API.get(`/api/cards/${cardId}/comments`),
    addComment: (cardId, data) => API.post(`/api/cards/${cardId}/comments`, data)
};
