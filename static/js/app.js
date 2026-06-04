document.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;
    
    // Инициализируем страницу
    if (path === '/login') {
        // Страница логина - не требуем авторизацию
        Auth.init();
    } else if (path.match(/^\/boards\/\d+$/)) {
        const boardId = parseInt(path.split('/').pop());
        Auth.init().then(() => Board.init(boardId));
    } else if (path.match(/^\/teams\/\d+$/)) {
        const teamId = parseInt(path.split('/').pop());
        Auth.init().then(() => Teams.init(teamId));
    } else if (path === '/boards') {
        Auth.init().then(() => loadBoardsList());
    } else if (path === '/teams') {
        Auth.init().then(() => loadTeamsList());
    } else {
        Auth.init();
    }
});

async function loadBoardsList() {
    try {
        const boards = await API.getBoards();
        const container = document.getElementById('boards-container');
        if (!container) return;
        
        container.innerHTML = boards.map(board => `
            <div class="card">
                <h3>${board.title}</h3>
                <p style="color: #5e6c84; margin: 0.5rem 0;">${board.description || 'No description'}</p>
                <a href="/boards/${board.id}" class="btn">Open Board</a>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading boards:', error);
    }
}

async function loadTeamsList() {
    try {
        const teams = await API.getTeams();
        const container = document.getElementById('teams-container');
        if (!container) return;
        
        container.innerHTML = teams.map(team => `
            <div class="card">
                <h3>${team.name}</h3>
                <p style="color: #5e6c84; margin: 0.5rem 0;">${team.description || 'No description'}</p>
                <p style="font-size: 0.9rem; color: #5e6c84;">Members: ${team.members.length}</p>
                <a href="/teams/${team.id}" class="btn" style="margin-top: 0.5rem;">View Team</a>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading teams:', error);
    }
}