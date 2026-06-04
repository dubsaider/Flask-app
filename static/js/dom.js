const DOM = {
    clone(templateId) {
        const template = document.getElementById(templateId);
        if (!template) {
            console.error(`Template not found: ${templateId}`);
            return document.createDocumentFragment();
        }
        return template.content.cloneNode(true);
    },

    clear(element) {
        element.replaceChildren();
    },

    show(element) {
        element?.classList.remove('hidden');
    },

    hide(element) {
        element?.classList.add('hidden');
    },

    setText(element, selector, text) {
        const node = element.querySelector(selector);
        if (node) node.textContent = text;
    },

    setField(root, field, value) {
        const node = root.querySelector(`[data-field="${field}"]`);
        if (!node) return;
        if (node.tagName === 'INPUT' || node.tagName === 'TEXTAREA') {
            node.value = value;
        } else {
            node.textContent = value;
        }
    },

    toggle(element, visible) {
        if (visible) {
            this.show(element);
        } else {
            this.hide(element);
        }
    }
};
