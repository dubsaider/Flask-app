const Teams = {
    teamId: null,
    currentTeam: null,
    
    init(teamId) {
        this.teamId = teamId;
        this.load();
    },
    
    async load() {
        try {
            const team = await API.getTeam(this.teamId);
            this.currentTeam = team;
            window.currentTeam = team;
            
            // Проверяем авторизацию
            if (!Auth.isAuthenticated()) {
                this.showAccessDenied('Please login to view this team');
                return;
            }
            
            const userRole = Auth.getUserRole(team);
            if (userRole === 'none') {
                this.showAccessDenied('You are not a member of this team');
                return;
            }
            
            const boards = await API.getTeamBoards(this.teamId);
            this.render(team, boards);
            this.loadAvailableUsers(team);
            
        } catch (error) {
            console.error('Error loading team:', error);
            this.showError('Error loading team: ' + error.message);
        }
    },
        
    showAccessDenied(message) {
        const container = document.getElementById('team-detail');
        if (!container) return;
        
        container.innerHTML = `
            <div class="card" style="text-align: center; padding: 3rem; margin-top: 2rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🔒</div>
                <h2 style="margin-bottom: 1rem; color: #eb5a46;">Access Denied</h2>
                <p style="color: #5e6c84; margin-bottom: 2rem;">${message}</p>
                <div style="display: flex; gap: 1rem; justify-content: center;">
                    <a href="/teams" class="btn btn-secondary">← Back to Teams</a>
                    <a href="/login" class="btn">Login</a>
                </div>
            </div>
        `;
    },
    
    showError(message) {
        const container = document.getElementById('team-detail');
        if (!container) return;
        
        container.innerHTML = `
            <div class="card" style="text-align: center; padding: 3rem; margin-top: 2rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">⚠️</div>
                <h2 style="margin-bottom: 1rem;">Error</h2>
                <p style="color: #5e6c84; margin-bottom: 2rem;">${message}</p>
                <a href="/teams" class="btn btn-secondary">← Back to Teams</a>
            </div>
        `;
    },
    
    render(team, boards) {
        const userRole = Auth.getUserRole(team);
        
        const curatorHTML = team.curator ? `
            <div class="member-card" style="border: 2px solid #4a90e2;">
                <div class="member-avatar" style="background-color: #4a90e2; color: white;">
                    ${team.curator.username.charAt(0).toUpperCase()}
                </div>
                <div class="member-info">
                    <div class="member-name">${team.curator.username}</div>
                    <div class="member-email">${team.curator.email}</div>
                </div>
                <span class="member-role role-curator">Curator</span>
            </div>
        ` : '<p style="color: #5e6c84;">No curator assigned</p>';
        
        const membersHTML = team.members.map(member => `
            <div class="member-card">
                <div class="member-avatar">
                    ${member.username.charAt(0).toUpperCase()}
                </div>
                <div class="member-info">
                    <div class="member-name">${member.username}</div>
                    <div class="member-email">${member.email}</div>
                </div>
                <span class="member-role role-${member.role}">${member.role}</span>
                ${userRole === 'leader' ? 
                    `<button class="btn-icon" onclick="Teams.removeMember(${member.id})">✕</button>` : ''}
            </div>
        `).join('');
        
        const boardsHTML = boards.length ? boards.map(board => `
            <div class="card">
                <h3>${board.title}</h3>
                <p style="color: #5e6c84; margin: 0.5rem 0;">
                    ${board.description || 'No description'}
                </p>
                <a href="/boards/${board.id}" class="btn">Open Board</a>
            </div>
        `).join('') : '<p style="color: #5e6c84;">No boards yet</p>';
        
        const roleLabels = {
            'leader': '👑 You are the Team Leader',
            'developer': '👨‍💻 You are a Developer',
            'curator': '👁️ You are the Curator (Observer)'
        };
        
        const roleInfo = roleLabels[userRole] ? `
            <div style="
                display: inline-block;
                padding: 0.5rem 1rem;
                background: ${userRole === 'curator' ? '#4a90e2' : userRole === 'leader' ? '#ffd700' : '#dfe1e6'};
                color: ${userRole === 'leader' ? '#172b4d' : 'white'};
                border-radius: 3px;
                margin-bottom: 1rem;
                font-weight: 500;
            ">
                ${roleLabels[userRole]}
            </div>
        ` : '';
        
        document.getElementById('team-detail').innerHTML = `
            <div class="team-header">
                <h1 class="team-title">${team.name}</h1>
                <p class="team-description">${team.description || 'No description'}</p>
                ${roleInfo}
                ${userRole === 'leader' ? 
                    `<button class="btn btn-danger" onclick="Teams.deleteTeam()" style="margin-top: 1rem;">Delete Team</button>` : ''}
            </div>
            
            ${team.curator_id ? `
                <h2 class="section-title">Curator</h2>
                <div class="members-grid">${curatorHTML}</div>
            ` : ''}
            
            <h2 class="section-title">
                Members (${team.members.length})
                ${userRole === 'leader' ? 
                    '<button class="btn" onclick="Modals.openAddMember()">+ Add Member</button>' : ''}
            </h2>
            <div class="members-grid">${membersHTML}</div>
            
            <h2 class="section-title">Boards (${boards.length})</h2>
            <div class="grid">${boardsHTML}</div>
            
            <div style="margin-top: 2rem;">
                <a href="/teams" class="btn btn-secondary">← Back to Teams</a>
            </div>
        `;
    },
    
    async loadAvailableUsers(team) {
        const users = await API.getUsers();
        const select = document.getElementById('user-select');
        if (!select) return;
        
        select.innerHTML = '<option value="">Choose user...</option>';
        const memberIds = team.members.map(m => m.id);
        
        users.forEach(user => {
            if (!memberIds.includes(user.id) && user.id !== team.curator_id) {
                const option = document.createElement('option');
                option.value = user.id;
                option.textContent = user.username;
                select.appendChild(option);
            }
        });
    },
    
    async addMember(event) {
        event.preventDefault();
        const userId = document.getElementById('user-select').value;
        const role = document.getElementById('role-select').value;
        
        if (!userId) return;
        
        try {
            await API.addMember(this.teamId, { 
                user_id: parseInt(userId), 
                role 
            });
            Modals.closeAddMember();
            this.load();
        } catch (error) {
            alert('Error adding member: ' + error.message);
        }
    },
    
    async removeMember(userId) {
        if (!confirm('Remove this member?')) return;
        
        try {
            await API.removeMember(this.teamId, userId);
            this.load();
        } catch (error) {
            alert('Error removing member: ' + error.message);
        }
    },
    
    async deleteTeam() {
        if (!confirm('Delete this team and all its boards?')) return;
        
        try {
            await API.deleteTeam(this.teamId);
            window.location.href = '/teams';
        } catch (error) {
            alert('Error deleting team: ' + error.message);
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('add-member-form')?.addEventListener('submit', (e) => Teams.addMember(e));
});