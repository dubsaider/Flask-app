const RichText = {
    editors: {},
    maxImageSize: window.APP_CONFIG?.richTextMaxImageSize ?? 512000,

    cardToolbar: [
        [{ header: [1, 2, 3, false] }],
        ['bold', 'italic', 'underline', 'strike'],
        [{ list: 'ordered' }, { list: 'bullet' }],
        ['link', 'image'],
        ['clean']
    ],

    commentToolbar: [
        ['bold', 'italic', 'underline'],
        [{ list: 'ordered' }, { list: 'bullet' }],
        ['link', 'image'],
        ['clean']
    ],

    init() {
        if (typeof Quill === 'undefined') return;
        this.initCardEditor();
        this.initCommentEditor();
    },

    initCardEditor() {
        const container = document.getElementById('card-description-editor');
        const hidden = document.getElementById('card-description-input');
        if (!container || this.editors.card) return;

        this.editors.card = new Quill(container, {
            theme: 'snow',
            placeholder: Locale.get('rich_text.card_placeholder'),
            modules: { toolbar: this.cardToolbar }
        });

        this.bindImageUpload(this.editors.card);
        this.editors.card.on('text-change', () => {
            hidden.value = this.getEditorHtml(this.editors.card);
        });
    },

    initCommentEditor() {
        const container = document.getElementById('comment-editor');
        const hidden = document.getElementById('comment-text-input');
        if (!container || this.editors.comment) return;

        this.editors.comment = new Quill(container, {
            theme: 'snow',
            placeholder: Locale.get('comments.editor_placeholder'),
            modules: { toolbar: this.commentToolbar }
        });

        this.bindImageUpload(this.editors.comment);
        this.editors.comment.on('text-change', () => {
            hidden.value = this.getEditorHtml(this.editors.comment);
        });
    },

    bindImageUpload(quill) {
        const toolbar = quill.getModule('toolbar');
        if (!toolbar) return;

        toolbar.addHandler('image', () => {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = 'image/*';
            input.onchange = () => {
                const file = input.files?.[0];
                if (!file) return;
                if (file.size > this.maxImageSize) {
                    alert(Locale.get('rich_text.image_too_large'));
                    return;
                }
                const reader = new FileReader();
                reader.onload = () => {
                    const range = quill.getSelection(true);
                    quill.insertEmbed(range.index, 'image', reader.result, Quill.sources.USER);
                    quill.setSelection(range.index + 1);
                };
                reader.readAsDataURL(file);
            };
            input.click();
        });
    },

    getEditorHtml(quill) {
        const html = quill.root.innerHTML.trim();
        if (html === '<p><br></p>' || html === '<p></p>') return '';
        return html;
    },

    setCardContent(html) {
        this.initCardEditor();
        const editor = this.editors.card;
        const hidden = document.getElementById('card-description-input');
        if (!editor) return;

        if (html && html.includes('<')) {
            editor.root.innerHTML = html;
        } else {
            editor.setText(html || '');
        }
        hidden.value = this.getEditorHtml(editor);
    },

    clearCard() {
        if (this.editors.card) {
            this.editors.card.setText('');
        }
        const hidden = document.getElementById('card-description-input');
        if (hidden) hidden.value = '';
    },

    getCardContent() {
        if (this.editors.card) {
            return this.getEditorHtml(this.editors.card);
        }
        return document.getElementById('card-description-input')?.value || '';
    },

    setCommentContent(html) {
        this.initCommentEditor();
        const editor = this.editors.comment;
        if (!editor) return;

        if (html && html.includes('<')) {
            editor.root.innerHTML = html;
        } else {
            editor.setText(html || '');
        }
        document.getElementById('comment-text-input').value = this.getEditorHtml(editor);
    },

    clearComment() {
        if (this.editors.comment) {
            this.editors.comment.setText('');
        }
        const hidden = document.getElementById('comment-text-input');
        if (hidden) hidden.value = '';
    },

    getCommentContent() {
        if (this.editors.comment) {
            return this.getEditorHtml(this.editors.comment);
        }
        return document.getElementById('comment-text-input')?.value || '';
    },

    renderHtml(element, html) {
        if (!element) return;
        element.classList.add('rich-text-content');
        if (!html) {
            element.innerHTML = '';
            return;
        }
        if (html.includes('<')) {
            element.innerHTML = html;
        } else {
            element.textContent = html;
        }
    },

    stripHtml(html) {
        if (!html) return '';
        const tmp = document.createElement('div');
        tmp.innerHTML = html;
        return tmp.textContent || tmp.innerText || '';
    }
};

document.addEventListener('DOMContentLoaded', () => RichText.init());
