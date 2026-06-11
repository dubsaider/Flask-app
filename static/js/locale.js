/**
 * UI-тексты из window.APP_CONFIG.labels (сервер labels.py).
 */
const Locale = {
    get data() {
        return window.APP_CONFIG?.labels || {};
    },

    get(path, fallback = '') {
        const value = path.split('.').reduce((obj, key) => obj?.[key], this.data);
        return value ?? fallback;
    },

    format(path, vars = {}) {
        let text = this.get(path, path);
        Object.entries(vars).forEach(([key, value]) => {
            text = text.replace(new RegExp(`\\{${key}\\}`, 'g'), String(value));
        });
        return text;
    },

    apply(root = document) {
        root.querySelectorAll('[data-label]').forEach((node) => {
            const key = node.dataset.label;
            const value = this.get(key);
            if (value) node.textContent = value;
        });
        root.querySelectorAll('[data-label-placeholder]').forEach((node) => {
            const value = this.get(node.dataset.labelPlaceholder);
            if (value) node.placeholder = value;
        });
        root.querySelectorAll('[data-label-title]').forEach((node) => {
            const value = this.get(node.dataset.labelTitle);
            if (value) {
                node.title = value;
                if (node.hasAttribute('aria-label')) node.setAttribute('aria-label', value);
            }
        });
    },

    priority(key) {
        return this.data.enums?.priority?.[key] || key;
    },

    workflow(key) {
        return this.data.enums?.workflow?.[key] || key;
    },

    role(key) {
        return this.data.enums?.roles?.[key] || key;
    },

    roleDescription(key) {
        return this.data.enums?.role_descriptions?.[key] || '';
    },

    permission(key) {
        return this.data.enums?.permissions?.[key] || key;
    }
};

document.addEventListener('DOMContentLoaded', () => Locale.apply());
