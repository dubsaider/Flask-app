const Auth = {
    currentUser: null,
    allUsers: [],
    
    async init() {
        // Загружаем список всех пользователей
        try {
            this.allUsers = await API.getUsers();
        } catch (error) {
            console.error('Error loading users:', error);
            this.allUsers = [];
        }
        
        const savedUserId = localStorage.getItem('currentUserId');
        const savedUsername = localStorage.getItem('currentUsername');
        
        if (savedUserId && savedUsername) {
            this.currentUser = {
                id: parseInt(savedUserId),
                username: savedUsername
            };
        } else {
            this.currentUser = null;
        }
        
        this.renderNavbar();
    },
    
    login(userId, username) {
        this.currentUser = { id: userId, username };
        localStorage.setItem('currentUserId', userId);
        localStorage.setItem('currentUsername', username);
        this.renderNavbar();
        
        if (window.location.pathname === '/login') {
            window.location.href = '/';
        } else {
            location.reload();
        }
    },
    
    logout() {
        this.currentUser = null;
        localStorage.removeItem('currentUserId');
        localStorage.removeItem('currentUsername');
        this.renderNavbar();
        
        // Перезагружаем текущую страницу
        location.reload();
    },
    
    getCurrentUser() {
        return this.currentUser;
    },
    
    isAuthenticated() {
        return this.currentUser !== null;
    },
    
    isTeamMember(teamMembers) {
        if (!this.currentUser) return false;
        return teamMembers?.some(m => m.id === this.currentUser.id) || false;
    },
    
    isTeamLeader(teamMembers) {
        if (!this.currentUser) return false;
        return teamMembers?.some(m => m.id === this.currentUser.id && m.role === 'leader') || false;
    },
    
    isCurator(team) {
        if (!this.currentUser || !team) return false;
        return team.curator_id === this.currentUser.id;
    },
    
    getUserRole(team) {
        if (!this.currentUser || !team) return 'none';
        
        if (team.curator_id === this.currentUser.id) return 'curator';
        
        const member = team.members?.find(m => m.id === this.currentUser.id);
        if (member) return member.role;
        
        return 'none';
    },
    
    renderNavbar() {
        const navUser = document.getElementById('nav-user');
        if (!navUser) return;
        
        if (this.isAuthenticated()) {
            // Пользователь авторизован - показываем меню пользователя
            navUser.innerHTML = `
                <div class="user-menu">
                    <button class="user-button" id="user-button">
                        <span class="user-avatar-small">${this.currentUser.username.charAt(0).toUpperCase()}</span>
                        <span>${this.currentUser.username}</span>
                        <span class="dropdown-arrow">▼</span>
                    </button>
                    <div class="user-dropdown" id="user-dropdown" style="display:none;">
                        <div class="dropdown-header">Current User</div>
                        <div class="user-item active">
                            <div class="user-item-avatar">${this.currentUser.username.charAt(0).toUpperCase()}</div>
                            <div class="user-item-info">
                                <div class="user-item-name">${this.currentUser.username}</div>
                                <div class="user-item-email">Current user</div>
                            </div>
                            <span style="color:#026aa7;">✓</span>
                        </div>
                        <div style="border-top: 1px solid #dfe1e6;">
                            <button class="user-item" onclick="Auth.logout()" style="color: #eb5a46;">
                                <span style="margin-right: 0.5rem;">🚪</span>
                                Logout
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
            // Добавляем обработчик для открытия/закрытия меню
            setTimeout(() => {
                const userButton = document.getElementById('user-button');
                const userDropdown = document.getElementById('user-dropdown');
                
                if (userButton && userDropdown) {
                    userButton.addEventListener('click', (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        
                        if (userDropdown.style.display === 'none') {
                            userDropdown.style.display = 'block';
                        } else {
                            userDropdown.style.display = 'none';
                        }
                    });
                    
                    // Закрываем меню при клике вне его
                    document.addEventListener('click', (e) => {
                        if (!userButton.contains(e.target) && !userDropdown.contains(e.target)) {
                            userDropdown.style.display = 'none';
                        }
                    });
                }
            }, 100);
            
        } else {
            // Гость - показываем кнопку Login
            navUser.innerHTML = `
                <a href="/login" class="btn" style="background: white; color: #026aa7; font-weight: 500;">
                    Login
                </a>
            `;
        }
    }
};