const enums = () => window.APP_CONFIG?.labels?.enums || {};

const PRIORITY_LABELS = enums().priority || {};
const ROLE_LABELS = enums().roles || {};
const ROLE_DESCRIPTIONS = enums().role_descriptions || {};
const PERMISSION_LABELS = enums().permissions || {};
const WORKFLOW_LABELS = enums().workflow || {};
const TEMPLATE_PERMISSIONS = window.APP_CONFIG?.roleTemplates || {};

const TaskWorkflow = {
    status(card) {
        if (card.workflow_status) return card.workflow_status;
        if (card.status === 'archived') return 'archived';
        if (card.is_completed || card.column_is_done) return 'completed';
        return 'active';
    },

    label(card) {
        return WORKFLOW_LABELS[this.status(card)] || this.status(card);
    }
};
