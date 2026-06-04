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

    getTeam: (id) => API.get(`/api/teams/${id}`),

    getBoard: (id) => API.get(`/api/boards/${id}`),
    updateBoard: (id, data) => API.put(`/api/boards/${id}`, data),
    deleteBoard: (id) => API.delete(`/api/boards/${id}`),
    getColumns: (boardId) => API.get(`/api/boards/${boardId}/columns`),

    createColumn: (boardId, data) => API.post(`/api/boards/${boardId}/columns`, data),
    updateColumn: (id, data) => API.put(`/api/columns/${id}`, data),
    deleteColumn: (id) => API.delete(`/api/columns/${id}`),

    getCard: (id) => API.get(`/api/cards/${id}`),
    createCard: (data) => API.post('/api/cards', data),
    updateCard: (id, data) => API.put(`/api/cards/${id}`, data),
    deleteCard: (id) => API.delete(`/api/cards/${id}`),
    moveCard: (id, data) => API.put(`/api/cards/${id}/move`, data),

    getComments: (cardId) => API.get(`/api/cards/${cardId}/comments`),
    addComment: (cardId, data) => API.post(`/api/cards/${cardId}/comments`, data)
};
