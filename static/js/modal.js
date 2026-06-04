// Управление модальными окнами
const Modals = {
    // Card modal
    openCard(cardId = null, columnId = null) {
        const modal = document.getElementById('card-modal');
        if (!modal) return;
        
        const currentTeam = window.currentTeam;
        const userRole = Auth.getUserRole(currentTeam);
        
        // Показываем/скрываем элементы в зависимости от роли
        document.querySelectorAll('.curator-only').forEach(el => {
            el.style.display = userRole === 'curator' ? 'block' : 'none';
        });
        
        document.querySelectorAll('.member-only').forEach(el => {
            el.style.display = ['leader', 'developer'].includes(userRole) ? 'flex' : 'none';
        });
        
        document.querySelectorAll('.leader-only').forEach(el => {
            el.style.display = userRole === 'leader' ? 'block' : 'none';
        });
        
        if (cardId) {
            Cards.loadCardForEdit(cardId);
        } else {
            this.prepareNewCard(columnId);
        }
        
        modal.classList.add('active');
    },
    
    closeCard() {
        document.getElementById('card-modal').classList.remove('active');
    },
    
    prepareNewCard(columnId) {
        document.getElementById('card-modal-title').textContent = 'Create Card';
        document.getElementById('card-id').value = '';
        document.getElementById('card-column-id').value = columnId;
        document.getElementById('card-title-input').value = '';
        document.getElementById('card-description-input').value = '';
        document.getElementById('card-priority-input').value = 'medium';
        document.getElementById('card-status-input').value = 'active';
        document.getElementById('card-deadline-input').value = '';
        document.getElementById('card-form').style.display = '';
        document.getElementById('card-view-only').style.display = 'none';
        document.getElementById('comments-list').innerHTML = '';
        Cards.populateAssigneeSelect(null);
    },
    
    // Board modal
    openBoard() {
        const board = window.currentBoard;
        if (board) {
            document.getElementById('board-title-input').value = board.title;
            document.getElementById('board-description-input').value = board.description || '';
        }
        document.getElementById('board-modal').classList.add('active');
    },
    
    closeBoard() {
        document.getElementById('board-modal').classList.remove('active');
    },
    
    // Column modal
    openColumn(columnId, currentTitle) {
        document.getElementById('column-id').value = columnId;
        document.getElementById('column-title-input').value = currentTitle;
        document.getElementById('column-modal').classList.add('active');
    },
    
    closeColumn() {
        document.getElementById('column-modal').classList.remove('active');
    },
    
    // Member modal
    openAddMember() {
        document.getElementById('add-member-modal').classList.add('active');
    },
    
    closeAddMember() {
        document.getElementById('add-member-modal').classList.remove('active');
    }
};

// Закрытие по клику вне модального окна
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.classList.remove('active');
    }
};