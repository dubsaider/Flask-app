"""SQLAlchemy-схема БД (источник истины для Alembic)."""
from datetime import datetime

from extensions import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password_hash = db.Column(db.String, nullable=False, default='hash')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    curator_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class TeamRole(db.Model):
    __tablename__ = 'team_roles'
    __table_args__ = (db.UniqueConstraint('team_id', 'slug', name='uq_team_roles_team_slug'),)

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String, nullable=False)
    slug = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    permissions = db.Column(db.Text, nullable=False, default='{}')
    is_system = db.Column(db.Boolean, nullable=False, default=False)
    template_key = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class TeamMember(db.Model):
    __tablename__ = 'team_members'

    team_id = db.Column(db.Integer, db.ForeignKey('teams.id', ondelete='CASCADE'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('team_roles.id', ondelete='RESTRICT'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)


class Board(db.Model):
    __tablename__ = 'boards'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Column(db.Model):
    __tablename__ = 'columns'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    position = db.Column(db.Integer, nullable=False)
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id', ondelete='CASCADE'), nullable=False)
    is_done = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Card(db.Model):
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    position = db.Column(db.Integer, nullable=False)
    column_id = db.Column(db.Integer, db.ForeignKey('columns.id', ondelete='CASCADE'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    priority = db.Column(db.String, default='medium')
    status = db.Column(db.String, default='active')
    deadline = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id', ondelete='SET NULL'))
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id', ondelete='SET NULL'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
