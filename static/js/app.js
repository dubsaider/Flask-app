document.addEventListener('DOMContentLoaded', async () => {
    const boardApp = document.getElementById('board-app');
    if (!boardApp) return;

    const isAuthed = await Auth.requireAuth();
    if (!isAuthed) return;

    const boardId = parseInt(boardApp.dataset.boardId, 10);
    await Sidebar.init(boardId);
    Board.init(boardId);
});
