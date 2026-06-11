from models.orm_utils import attr


class User:
    """DTO пользователя."""
    def __init__(self, row):
        self.id = attr(row, 'id')
        self.username = attr(row, 'username')
        self.email = attr(row, 'email')
        self.created_at = attr(row, 'created_at')
        self.role = attr(row, 'role')

    def to_dict(self):
        result = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else self.created_at,
        }
        if self.role:
            result['role'] = self.role
        if hasattr(self, 'role_id') and self.role_id:
            result['role_id'] = self.role_id
        if hasattr(self, 'role_name') and self.role_name:
            result['role_name'] = self.role_name
        return result


class Team:
    """DTO команды."""
    def __init__(self, row):
        self.id = attr(row, 'id')
        self.name = attr(row, 'name')
        self.description = attr(row, 'description')
        self.curator_id = attr(row, 'curator_id')
        self.created_at = attr(row, 'created_at')
        self.members = []
        self.curator = None
        self.roles = []

    def to_dict(self):
        result = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'curator_id': self.curator_id,
            'created_at': self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else self.created_at,
            'members': [m.to_dict() for m in self.members],
            'roles': self.roles,
        }
        if self.curator:
            result['curator'] = self.curator.to_dict()
        return result


class Board:
    """DTO доски."""
    def __init__(self, row):
        self.id = attr(row, 'id')
        self.title = attr(row, 'title')
        self.description = attr(row, 'description')
        self.team_id = attr(row, 'team_id')
        self.created_at = attr(row, 'created_at')

    def to_dict(self):
        created = self.created_at
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'team_id': self.team_id,
            'created_at': created.isoformat() if hasattr(created, 'isoformat') else created,
        }


class Column:
    """DTO колонки."""
    def __init__(self, row):
        self.id = attr(row, 'id')
        self.title = attr(row, 'title')
        self.position = attr(row, 'position')
        self.board_id = attr(row, 'board_id')
        self.is_done = bool(attr(row, 'is_done', False))
        self.created_at = attr(row, 'created_at')
        self.cards = []

    def to_dict(self):
        created = self.created_at
        return {
            'id': self.id,
            'title': self.title,
            'position': self.position,
            'board_id': self.board_id,
            'is_done': self.is_done,
            'created_at': created.isoformat() if hasattr(created, 'isoformat') else created,
            'cards': [c.to_dict(column_is_done=self.is_done) for c in self.cards],
        }


class Card:
    """DTO карточки."""
    def __init__(self, row):
        self.id = attr(row, 'id')
        self.title = attr(row, 'title')
        self.description = attr(row, 'description')
        self.position = attr(row, 'position')
        self.column_id = attr(row, 'column_id')
        self.assignee_id = attr(row, 'assignee_id')
        self.created_by = attr(row, 'created_by')
        self.priority = attr(row, 'priority')
        self.status = attr(row, 'status')
        self.deadline = attr(row, 'deadline')
        self.created_at = attr(row, 'created_at')
        self.updated_at = attr(row, 'updated_at')
        self.assignee = None
        self.creator = None
        self.comments = []

    def to_dict(self, column_is_done=False):
        from api.card_helpers import workflow_fields
        wf = workflow_fields(self.status, column_is_done)
        created = self.created_at
        updated = self.updated_at
        deadline = self.deadline
        result = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'position': self.position,
            'column_id': self.column_id,
            'assignee_id': self.assignee_id,
            'created_by': self.created_by,
            'priority': self.priority,
            'status': wf['status'],
            'workflow_status': wf['workflow_status'],
            'is_completed': wf['is_completed'],
            'deadline': deadline.isoformat() if hasattr(deadline, 'isoformat') else deadline,
            'created_at': created.isoformat() if hasattr(created, 'isoformat') else created,
            'updated_at': updated.isoformat() if hasattr(updated, 'isoformat') else updated,
            'comments': [c.to_dict() for c in self.comments],
        }
        if self.assignee:
            result['assignee'] = self.assignee.to_dict()
        if self.creator:
            result['creator'] = self.creator.to_dict()
        return result


class Comment:
    """DTO комментария."""
    def __init__(self, row):
        self.id = attr(row, 'id')
        self.text = attr(row, 'text')
        self.card_id = attr(row, 'card_id')
        self.user_id = attr(row, 'user_id')
        self.created_at = attr(row, 'created_at')
        self.author = None

    def to_dict(self):
        created = self.created_at
        result = {
            'id': self.id,
            'text': self.text,
            'card_id': self.card_id,
            'user_id': self.user_id,
            'created_at': created.isoformat() if hasattr(created, 'isoformat') else created,
        }
        if self.author:
            result['author'] = self.author.to_dict()
        return result


class Notification:
    """DTO уведомления."""
    def __init__(self, row):
        self.id = attr(row, 'id')
        self.user_id = attr(row, 'user_id')
        self.message = attr(row, 'message')
        self.is_read = bool(attr(row, 'is_read', False))
        self.board_id = attr(row, 'board_id')
        self.card_id = attr(row, 'card_id')
        self.created_at = attr(row, 'created_at')

    def to_dict(self):
        created = self.created_at
        return {
            'id': self.id,
            'user_id': self.user_id,
            'message': self.message,
            'is_read': self.is_read,
            'board_id': self.board_id,
            'card_id': self.card_id,
            'created_at': created.isoformat() if hasattr(created, 'isoformat') else created,
        }
