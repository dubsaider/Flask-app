class User:
    """Простая модель пользователя"""
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
    """Простая модель команды"""
    def __init__(self, row):
        self.id = row['id']
        self.name = row['name']
        self.description = row['description']
        self.created_at = row['created_at']
        self.members = []  # Будет заполняться отдельно
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at,
            'members': [m.to_dict() for m in self.members]
        }

class Board:
    """Простая модель доски"""
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