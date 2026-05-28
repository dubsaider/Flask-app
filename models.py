class User:
    def __init__(self, row):
        self.id = row['id']
        self.username = row['username']
        self.email = row['email']
        self.created_at = row['created_at']
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at
        }

class Team:
    def __init__(self, row):
        self.id = row['id']
        self.name = row['name']
        self.description = row['description']
        self.created_at = row['created_at']
        self.members = []
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at,
            'members': [m.to_dict() for m in self.members]
        }

class Board:
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
    def __init__(self, row):
        self.id = row['id']
        self.title = row['title']
        self.description = row['description']
        self.position = row['position']
        self.column_id = row['column_id']
        self.assignee_id = row['assignee_id']
        self.priority = row['priority']
        self.created_at = row['created_at']
        self.updated_at = row['updated_at']
        self.assignee = None
    
    def to_dict(self):
        result = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'position': self.position,
            'column_id': self.column_id,
            'assignee_id': self.assignee_id,
            'priority': self.priority,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        if self.assignee:
            result['assignee'] = self.assignee.to_dict()
        return result