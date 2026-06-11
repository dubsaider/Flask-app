"""Безопасная очистка HTML из rich-text редактора."""
import re
from html.parser import HTMLParser
from html import escape

ALLOWED_TAGS = frozenset({
    'p', 'br', 'strong', 'b', 'em', 'i', 'u', 's', 'strike',
    'a', 'ul', 'ol', 'li', 'img', 'h1', 'h2', 'h3', 'blockquote', 'span',
})

VOID_TAGS = frozenset({'br', 'img'})

ALLOWED_ATTRS = {
    'a': frozenset({'href', 'title', 'target', 'rel'}),
    'img': frozenset({'src', 'alt', 'title'}),
    'span': frozenset({'class'}),
}

MAX_HTML_LENGTH = 50000
MAX_IMAGE_DATA_URL_LENGTH = 700000


def _limits():
    try:
        from flask import current_app
        return (
            current_app.config.get('MAX_HTML_LENGTH', MAX_HTML_LENGTH),
            current_app.config.get('MAX_IMAGE_DATA_URL_LENGTH', MAX_IMAGE_DATA_URL_LENGTH),
        )
    except RuntimeError:
        from config import get_config
        cfg = get_config()
        return cfg.MAX_HTML_LENGTH, cfg.MAX_IMAGE_DATA_URL_LENGTH


def _clean_href(value):
    if not value:
        return None
    value = value.strip()
    if value.startswith(('http://', 'https://', 'mailto:', '/', '#')):
        return value
    if value.startswith('data:image/'):
        _, max_len = _limits()
        if len(value) > max_len:
            return None
        return value
    return None


def _clean_src(value):
    if not value:
        return None
    value = value.strip()
    if value.startswith(('http://', 'https://', '/')):
        return value
    if value.startswith('data:image/'):
        _, max_len = _limits()
        if len(value) > max_len:
            return None
        return value
    return None


class _HTMLSanitizer(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.result = []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag not in ALLOWED_TAGS:
            self.skip_depth += 1
            return

        allowed = ALLOWED_ATTRS.get(tag, frozenset())
        clean_attrs = []
        for name, value in attrs:
            name = name.lower()
            if name not in allowed:
                continue
            if name == 'href':
                value = _clean_href(value)
            elif name == 'src':
                value = _clean_src(value)
            elif name == 'target' and value != '_blank':
                continue
            elif name == 'rel' and value != 'noopener noreferrer':
                value = 'noopener noreferrer'
            if value is None:
                continue
            clean_attrs.append(f'{name}="{escape(value, quote=True)}"')

        attr_str = f' {" ".join(clean_attrs)}' if clean_attrs else ''
        if tag in VOID_TAGS:
            self.result.append(f'<{tag}{attr_str}>')
        else:
            self.result.append(f'<{tag}{attr_str}>')

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag not in ALLOWED_TAGS:
            if self.skip_depth > 0:
                self.skip_depth -= 1
            return
        if tag in ALLOWED_TAGS and tag not in VOID_TAGS:
            self.result.append(f'</{tag}>')

    def handle_data(self, data):
        if self.skip_depth > 0:
            return
        self.result.append(escape(data))

    def get_html(self):
        return ''.join(self.result)


def plain_text_to_html(text):
    if not text:
        return ''
    if '<' in text and '>' in text:
        return sanitize_html(text)
    paragraphs = [escape(line) for line in text.split('\n')]
    return ''.join(f'<p>{part or "<br>"}</p>' for part in paragraphs)


def sanitize_html(html):
    if html is None:
        return ''
    html = str(html).strip()
    if not html:
        return ''
    max_html_len, _ = _limits()
    if len(html) > max_html_len:
        html = html[:max_html_len]

    if '<' not in html:
        return plain_text_to_html(html)

    parser = _HTMLSanitizer()
    parser.feed(html)
    parser.close()
    cleaned = parser.get_html().strip()
    return cleaned or ''


def html_to_plain_text(html):
    if not html:
        return ''
    text = re.sub(r'<\s*br\s*/?>', '\n', html, flags=re.I)
    text = re.sub(r'<[^>]+>', '', text)
    return re.sub(r'\n{3,}', '\n\n', text).strip()
