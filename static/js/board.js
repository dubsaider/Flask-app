// Логика канбан-доски
const Board = {
    boardId: null,
    currentBoard: null,
    currentTeam: null,
    
    init(boardId) {
        this.boardId = boardId;
        this.load();
    },
    
    async load() {
        try {
            this.currentBoard = await API.getBoard(this.boardId);
            document.getElementById('board-title').textContent = this.currentBoard.title;
            document.getElementById('board-description').textContent = this.currentBoard.description || '';
            
            this.currentTeam = await API.getTeam(this.currentBoard.team_id);
            window.currentTeam = this.currentTeam;
            window.currentBoard = this.currentBoard;
            
            // Проверяем авторизацию
            if (!Auth.isAuthenticated()) {
                this.showAccessDenied('Please login to view this board');
                return;
            }
            
            const userRole = Auth.getUserRole(this.currentTeam);
            if (userRole === 'none') {
                this.showAccessDenied('You are not a member of this team');
                return;
            }
            
            this.applyPermissions();
            this.showRoleInfo();
            this.loadColumns();
            
        } catch (error) {
            console.error('Error loading board:', error);
            this.showError('Error loading board: ' + error.message);
        }
    },
        
    showAccessDenied(message) {
        const container = document.getElementById('app');
        if (!container) return;
        
        container.innerHTML = `
            <div class="card" style="text-align: center; padding: 3rem; margin-top: 2rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🔒</div>
                <h2 style="margin-bottom: 1rem; color: #eb5a46;">Access Denied</h2>
                <p style="color: #5e6c84; margin-bottom: 2rem;">${message}</p>
                <div style="display: flex; gap: 1rem; justify-content: center;">
                    <a href="/boards" class="btn btn-secondary">← Back to Boards</a>
                    <a href="/login" class="btn">Login</a>
                </div>
            </div>
        `;
    },
    
    showError(message) {
        const container = document.getElementById('app');
        if (!container) return;
        
        container.innerHTML = `
            <div class="card" style="text-align: center; padding: 3rem; margin-top: 2rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">⚠️</div>
                <h2 style="margin-bottom: 1rem;">Error</h2>
                <p style="color: #5e6c84; margin-bottom: 2rem;">${message}</p>
                <a href="/boards" class="btn btn-secondary">← Back to Boards</a>
            </div>
        `;
    },
    
    applyPermissions() {
        const userRole = Auth.getUserRole(this.currentTeam);
        
        // Показываем/скрываем элементы в зависимости от роли
        document.querySelectorAll('.member-only').forEach(el => {
            el.style.display = ['leader', 'developer'].includes(userRole) ? '' : 'none';
        });
        
        document.querySelectorAll('.leader-only').forEach(el => {
            el.style.display = userRole === 'leader' ? '' : 'none';
        });
        
        // Если куратор - показываем специальные элементы
        document.querySelectorAll('.curator-only').forEach(el => {
            el.style.display = userRole === 'curator' ? '' : 'none';
        });
    },
    
    showRoleInfo() {
        const userRole = Auth.getUserRole(this.currentTeam);
        const header = document.querySelector('.board-header');
        if (!header) return;
        
        // Удаляем старую информацию о роли
        const oldRoleInfo = document.getElementById('role-info');
        if (oldRoleInfo) oldRoleInfo.remove();
        
        // Создаем новую
        const roleInfo = document.createElement('div');
        roleInfo.id = 'role-info';
        
        const roleLabels = {
            'leader': '👑 Team Leader',
            'developer': '👨‍💻 Developer',
            'curator': '👁️ Curator (View only)',
            'none': 'Not a team member'
        };
        
        const roleColors = {
            'leader': '#ffd700',
            'developer': '#dfe1e6',
            'curator': '#4a90e2',
            'none': '#eb5a46'
        };
        
        roleInfo.innerHTML = `
            <span style="
                display: inline-block;
                padding: 0.35rem 0.75rem;
                background: ${roleColors[userRole]};
                color: ${['leader', 'developer'].includes(userRole) ? '#172b4d' : 'white'};
                border-radius: 3px;
                font-size: 0.85rem;
                font-weight: 500;
            ">
                ${roleLabels[userRole]}
            </span>
        `;
        
        header.appendChild(roleInfo);
    },
    
    async loadColumns() {
        const columns = await API.getColumns(this.boardId);
        this.render(columns);
        
        // Инициализируем drag & drop только для участников команды
        const userRole = Auth.getUserRole(this.currentTeam);
        if (['leader', 'developer'].includes(userRole)) {
            DragDrop.init(columns);
        }
    },
    
    render(columns) {
        const container = document.getElementById('board-container');
        if (!container) return;
        
        const userRole = Auth.getUserRole(this.currentTeam);
        const canAddCards = ['leader', 'developer'].includes(userRole);
        const canManageColumns = ['leader', 'developer'].includes(userRole);
        
        let html = columns.map(column => `
            <div class="column" data-column-id="${column.id}">
                <div class="column-header">
                    <div class="column-title" 
                         ${canManageColumns ? `onclick="Modals.openColumn(${column.id}, '${column.title.replace(/'/g, "\\'")}')"` : ''}>
                        ${column.title}
                    </div>
                    ${canManageColumns ? 
                        `<button class="btn-icon" onclick="Modals.openColumn(${column.id}, '${column.title.replace(/'/g, "\\'")}')">⋯</button>` : ''}
                </div>
                <div class="cards-list" id="cards-${column.id}">
                    ${this.renderCards(column.cards || [])}
                </div>
                ${canAddCards ? `
                    <button class="add-card-btn" onclick="Modals.openCard(null, ${column.id})">
                        + Add a card
                    </button>
                ` : ''}
            </div>
        `).join('');
        
        if (canManageColumns) {
            html += `<button class="add-column-btn" onclick="Columns.add()">+ Add another list</button>`;
        }
        
        container.innerHTML = html;
    },
    
    renderCards(cards) {
        if (!cards.length) return '';
        
        return cards.map(card => `
            <div class="card-item" data-card-id="${card.id}" 
                 onclick="Modals.openCard(${card.id})">
                <div class="card-title">${card.title}</div>
                <div class="card-badges">
                    ${card.assignee ? 
                        `<span class="assignee-badge" title="${card.assignee.username}">
                            ${card.assignee.username.charAt(0).toUpperCase()}
                        </span>` : ''}
                    <span class="badge priority-${card.priority}">${card.priority}</span>
                    ${card.deadline ? '<span class="badge" style="background:#5e6c84;">📅</span>' : ''}
                    ${card.comments && card.comments.length > 0 ? 
                        `<span class="badge" style="background:#5e6c84;">💬${card.comments.length}</span>` : ''}
                </div>
            </div>
        `).join('');
    },
    
    async deleteBoard() {
        if (!confirm('Delete this board?')) return;
        await API.deleteBoard(this.boardId);
        window.location.href = '/boards';
    }
};

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('board-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        try {
            await API.updateBoard(Board.boardId, {
                title: document.getElementById('board-title-input').value,
                description: document.getElementById('board-description-input').value
            });
            Modals.closeBoard();
            Board.load();
        } catch (error) {
            alert('Error updating board: ' + error.message);
        }
    });
});