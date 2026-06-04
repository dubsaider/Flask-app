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
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error(await response.text());
        return response.json();
    },
    
    async put(url, data) {
        const response = await fetch(url, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
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
    
    // Users
    getUsers: () => API.get('/api/users'),
    
    // Teams
    getTeams: () => API.get('/api/teams'),
    getTeam: (id) => API.get(`/api/teams/${id}`),
    createTeam: (data) => API.post('/api/teams', data),
    updateTeam: (id, data) => API.put(`/api/teams/${id}`, data),
    deleteTeam: (id) => API.delete(`/api/teams/${id}`),
    addMember: (teamId, data) => API.post(`/api/teams/${teamId}/members`, data),
    removeMember: (teamId, userId) => API.delete(`/api/teams/${teamId}/members`, {user_id: userId}),
    getTeamBoards: (teamId) => API.get(`/api/teams/${teamId}/boards`),
    
    // Boards
    getBoards: () => API.get('/api/boards'),
    getBoard: (id) => API.get(`/api/boards/${id}`),
    createBoard: (data) => API.post('/api/boards', data),
    updateBoard: (id, data) => API.put(`/api/boards/${id}`, data),
    deleteBoard: (id) => API.delete(`/api/boards/${id}`),
    getColumns: (boardId) => API.get(`/api/boards/${boardId}/columns`),
    
    // Columns
    createColumn: (boardId, data) => API.post(`/api/boards/${boardId}/columns`, data),
    updateColumn: (id, data) => API.put(`/api/columns/${id}`, data),
    deleteColumn: (id) => API.delete(`/api/columns/${id}`),
    
    // Cards
    getCard: (id) => API.get(`/api/cards/${id}`),
    createCard: (data) => API.post('/api/cards', data),
    updateCard: (id, data) => API.put(`/api/cards/${id}`, data),
    deleteCard: (id) => API.delete(`/api/cards/${id}`),
    moveCard: (id, data) => API.put(`/api/cards/${id}/move`, data),
    
    // Comments
    getComments: (cardId) => API.get(`/api/cards/${cardId}/comments`),
    addComment: (cardId, data) => API.post(`/api/cards/${cardId}/comments`, data),
    deleteComment: (id) => API.delete(`/api/comments/${id}`)
};