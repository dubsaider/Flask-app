"""Утилиты для чтения ORM-моделей и Row."""


def attr(obj, name, default=None):
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(name, default)
    if hasattr(obj, '__getitem__'):
        try:
            return obj[name]
        except (KeyError, TypeError, IndexError):
            pass
    return getattr(obj, name, default)
