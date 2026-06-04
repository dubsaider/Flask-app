const LoginPage = {
    async init() {
        await Auth.init();

        if (Auth.isAuthenticated()) {
            await Auth.redirectToDefaultBoard();
            return;
        }

        await this.renderUsers();
    },

    async renderUsers() {
        const container = document.getElementById('login-users-list');
        if (!container) return;

        try {
            const users = await API.getUsers();
            DOM.clear(container);

            users.forEach(user => {
                const item = DOM.clone('tpl-login-user');
                const button = item.querySelector('.login-user-item');

                DOM.setField(item, 'avatar', user.username.charAt(0).toUpperCase());
                DOM.setField(item, 'name', user.username);
                DOM.setField(item, 'email', user.email);

                button.addEventListener('click', () => Auth.login(user.id, user.username));
                container.appendChild(item);
            });
        } catch (error) {
            console.error('Error loading users:', error);
            DOM.clear(container);
            const message = document.createElement('p');
            message.className = 'login-error';
            message.textContent = 'Не удалось загрузить пользователей';
            container.appendChild(message);
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    if (document.body.classList.contains('auth-body')) {
        LoginPage.init();
    }
});
