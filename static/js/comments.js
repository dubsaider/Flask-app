const Comments = {
    currentCardId: null,

    loadComments(cardId) {
        this.currentCardId = cardId;
        API.getComments(cardId).then(comments => this.render(comments));
    },

    render(comments) {
        const container = document.getElementById('comments-list');
        if (!container) return;

        DOM.clear(container);

        comments.forEach(comment => {
            const node = DOM.clone('tpl-comment-item');
            DOM.setField(node, 'author', comment.author?.username || 'Unknown');
            DOM.setField(node, 'date', new Date(comment.created_at).toLocaleString());
            DOM.setField(node, 'text', comment.text);
            container.appendChild(node);
        });
    },

    async addComment() {
        const textarea = document.getElementById('comment-text');
        const text = textarea.value.trim();

        if (!text || !this.currentCardId) return;

        try {
            await API.addComment(this.currentCardId, {
                text,
                user_id: Auth.getCurrentUser().id
            });

            textarea.value = '';
            this.loadComments(this.currentCardId);
        } catch (error) {
            console.error('Error adding comment:', error);
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('comment-submit-btn')?.addEventListener('click', () => Comments.addComment());
});
