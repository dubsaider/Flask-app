from datetime import datetime

class User:
    """Модель пользователя"""
    def __init__(self, row):
        self.id = row['id']
        self.username = row['username']
        self.email = row['email']
        self.created_at = row['created_at']
        self.role = row['role'] if 'role' in row.keys() else None
    
    def to_dict(self):
        result = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at
        }
        if self.role:
            result['role'] = self.role
        return result

class Team:
    """Модель команды"""
    def __init__(self, row):
        self.id = row['id']
        self.name = row['name']
        self.description = row['description']
        self.curator_id = row['curator_id']
        self.created_at = row['created_at']
        self.members = []
        self.curator = None
    
    def to_dict(self):
        result = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'curator_id': self.curator_id,
            'created_at': self.created_at,
            'members': [m.to_dict() for m in self.members]
        }
        if self.curator:
            result['curator'] = self.curator.to_dict()
        return result

class Board:
    """Модель доски"""
    def __init__(self, row):
        self.id = row['id']
        self.title = row['title']
        self.description = row['description']
        self.team_id = row['team_id']
        self.created_at = row['created_at']
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'team_id': self.team_id,
            'created_at': self.created_at
        }

class Column:
    """Модель колонки"""
    def __init__(self, row):
        self.id = row['id']
        self.title = row['title']
        self.position = row['position']
        self.board_id = row['board_id']
        self.created_at = row['created_at']
        self.cards = []
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'position': self.position,
            'board_id': self.board_id,
            'created_at': self.created_at,
            'cards': [c.to_dict() for c in self.cards]
        }

class Card:
    """Модель карточки/задачи"""
    def __init__(self, row):
        self.id = row['id']
        self.title = row['title']
        self.description = row['description']
        self.position = row['position']
        self.column_id = row['column_id']
        self.assignee_id = row['assignee_id']
        self.created_by = row['created_by']
        self.priority = row['priority']
        self.status = row['status']
        self.deadline = row['deadline']
        self.created_at = row['created_at']
        self.updated_at = row['updated_at']
        self.assignee = None
        self.creator = None
        self.comments = []
    
    def to_dict(self):
        result = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'position': self.position,
            'column_id': self.column_id,
            'assignee_id': self.assignee_id,
            'created_by': self.created_by,
            'priority': self.priority,
            'status': self.status,
            'deadline': self.deadline,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'comments': [c.to_dict() for c in self.comments]
        }
        if self.assignee:
            result['assignee'] = self.assignee.to_dict()
        if self.creator:
            result['creator'] = self.creator.to_dict()
        return result

class Comment:
    """Модель комментария"""
    def __init__(self, row):
        self.id = row['id']
        self.text = row['text']
        self.card_id = row['card_id']
        self.user_id = row['user_id']
        self.created_at = row['created_at']
        self.author = None
    
    def to_dict(self):
        result = {
            'id': self.id,
            'text': self.text,
            'card_id': self.card_id,
            'user_id': self.user_id,
            'created_at': self.created_at
        }
        if self.author:
            result['author'] = self.author.to_dict()
        return result