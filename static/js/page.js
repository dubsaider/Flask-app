document.addEventListener('DOMContentLoaded', async () => {
    if (!await Auth.requireAuth()) return;

    const boardApp = document.getElementById('board-app');
    const tasksApp = document.getElementById('tasks-app');
    const dashboardApp = document.getElementById('dashboard-app');

    if (boardApp) {
        const boardId = parseInt(boardApp.dataset.boardId, 10);
        await Sidebar.init(boardId, 'board');
        Board.init(boardId);
    } else if (tasksApp) {
        await Sidebar.init(null, 'tasks');
        TasksPage.init();
    } else if (dashboardApp) {
        await Sidebar.init(null, 'dashboard');
        DashboardPage.init();
    }
});
