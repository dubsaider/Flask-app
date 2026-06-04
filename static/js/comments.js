// Управление комментариями
const Comments = {
    currentCardId: null,
    
    loadComments(cardId) {
        this.currentCardId = cardId;
        API.getComments(cardId).then(comments => {
            this.render(comments);
        });
    },
    
    render(comments) {
        const container = document.getElementById('comments-list');
        if (!container) return;
        
        container.innerHTML = comments.map(comment => `
            <div class="comment-item">
                <div class="comment-header">
                    <span class="comment-author">${comment.author?.username || 'Unknown'}</span>
                    <span class="comment-date">${new Date(comment.created_at).toLocaleString()}</span>
                </div>
                <div class="comment-text">${comment.text}</div>
            </div>
        `).join('');
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