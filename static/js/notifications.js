const Notifications = {
    items: [],
    open: false,

    init() {
        this.bindEvents();
        this.refresh();
    },

    bindEvents() {
        document.getElementById('sidebar-notify-btn')?.addEventListener('click', (event) => {
            event.stopPropagation();
            this.togglePanel();
        });

        document.getElementById('notifications-read-all')?.addEventListener('click', () => {
            this.markAllRead();
        });

        document.addEventListener('click', (event) => {
            if (!this.open) return;
            const panel = document.getElementById('notifications-panel');
            const btn = document.getElementById('sidebar-notify-btn');
            if (panel?.contains(event.target) || btn?.contains(event.target)) return;
            this.closePanel();
        });
    },

    async refresh() {
        const user = Auth.getCurrentUser();
        if (!user) return;

        try {
            const [items, countData] = await Promise.all([
                API.getNotifications(user.id),
                API.getUnreadNotificationCount(user.id)
            ]);
            this.items = items;
            this.updateBadge(countData.count);
            if (this.open) this.renderList();
        } catch (error) {
            console.error('Error loading notifications:', error);
        }
    },

    togglePanel() {
        if (this.open) {
            this.closePanel();
        } else {
            this.openPanel();
        }
    },

    openPanel() {
        const panel = document.getElementById('notifications-panel');
        const btn = document.getElementById('sidebar-notify-btn');
        if (!panel) return;

        this.open = true;
        DOM.show(panel);
        btn?.setAttribute('aria-expanded', 'true');
        this.renderList();
    },

    closePanel() {
        const panel = document.getElementById('notifications-panel');
        const btn = document.getElementById('sidebar-notify-btn');
        this.open = false;
        DOM.hide(panel);
        btn?.setAttribute('aria-expanded', 'false');
    },

    renderList() {
        const container = document.getElementById('notifications-list');
        if (!container) return;

        DOM.clear(container);

        if (!this.items.length) {
            const empty = document.createElement('p');
            empty.className = 'notifications-panel__empty';
            empty.textContent = 'Нет уведомлений';
            container.appendChild(empty);
            return;
        }

        this.items.forEach(item => {
            const node = DOM.clone('tpl-notification-item');
            const btn = node.querySelector('[data-field="item"]');
            btn.classList.toggle('notification-item--unread', !item.is_read);
            DOM.setField(node, 'message', item.message);
            DOM.setField(node, 'time', this.formatTime(item.created_at));
            btn.addEventListener('click', () => this.handleItemClick(item));
            container.appendChild(node);
        });
    },

    updateBadge(count) {
        const badge = document.getElementById('sidebar-notify-badge');
        if (!badge) return;

        if (count > 0) {
            badge.textContent = count > 99 ? '99+' : String(count);
            DOM.show(badge);
        } else {
            DOM.hide(badge);
        }
    },

    async handleItemClick(item) {
        const user = Auth.getCurrentUser();
        if (!user) return;

        try {
            if (!item.is_read) {
                await API.markNotificationRead(item.id, user.id);
            }
            this.closePanel();

            if (item.board_id) {
                let url = `/board/${item.board_id}`;
                if (item.card_id) {
                    url += `?card=${item.card_id}`;
                }
                window.location.href = url;
                return;
            }

            await this.refresh();
        } catch (error) {
            console.error('Error handling notification:', error);
        }
    },

    async markAllRead() {
        const user = Auth.getCurrentUser();
        if (!user) return;

        try {
            await API.markAllNotificationsRead(user.id);
            await this.refresh();
        } catch (error) {
            console.error('Error marking all read:', error);
        }
    },

    formatTime(value) {
        if (!value) return '';
        const date = new Date(value.replace(' ', 'T'));
        if (Number.isNaN(date.getTime())) return value;

        const now = new Date();
        const diffMs = now - date;
        const diffMin = Math.floor(diffMs / 60000);

        if (diffMin < 1) return 'только что';
        if (diffMin < 60) return `${diffMin} мин. назад`;

        const diffHours = Math.floor(diffMin / 60);
        if (diffHours < 24) return `${diffHours} ч. назад`;

        return date.toLocaleDateString('ru-RU', {
            day: 'numeric',
            month: 'short',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
};
