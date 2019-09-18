from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.passwordHash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

# monitoring task
class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    description = db.Column(db.Text)

    url = db.Column(db.String(2048), index=True, unique=True)
    created_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    expiring_time = db.Column(db.DateTime, index=True)

    def __repr__(self):
        return '<Task {}>'.format(self.title)

# prices history
class Price(db.Model):
    __tablename__ ='prices'

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Numeric(10, 2))

subscribe_table = db.Table(
    'subscribes',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('task_id', db.Integer, db.ForeignKey('tasks.id')),
    db.PrimaryKeyConstraint('user_id', 'task_id')
)

price_lookup_table = db.Table(
    'price_lookup',
    db.Column('task_id', db.Integer, db.ForeignKey('tasks.id')),
    db.Column('price_id', db.Integer, db.ForeignKey('prices.id')),
    db.PrimaryKeyConstraint('task_id', 'price_id')
)