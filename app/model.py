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

    tasks = db.relationship("Task", secondary="subscribes")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.passwordHash, password)

    def subscribe(self, task, time=datetime.utcnow):
        self.subscribes.append(Subscribe(user=self, task=task, subscribe_time=time))

    def unsubscribe(self, task_id):
        for task in self.subscribes:
            if task.id == task_id:
                self.subscribes.remove(task)
                return True
        return False

    def __repr__(self):
        return '<User {} [{}]>'.format(self.name, self.id)

# monitoring task
class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(2048))

    url = db.Column(db.String(2048), index=True, unique=True)
    created_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    expiring_time = db.Column(db.DateTime, index=True)
    interval = db.Column(db.Integer, index=True) # frequency, in minutes

    prices = db.relationship("Price", secondary="price_lookup")
    subscribers = db.relationship("User", secondary="subscribes")

    def __repr__(self):
        return '<Task {} [{}]>'.format(self.name, self.id)

# prices history
class Price(db.Model):
    __tablename__ ='prices'

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    price = db.Column(db.Numeric(10, 2), index=True)


class Subscribe(db.Model):
    __tablename__ = 'subscribes'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), primary_key=True)
    subscribe_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("subscribes", cascade="all, delete-orphan" ))
    task = db.relationship("Task", backref=db.backref("subscribes", cascade="all, delete-orphan" ))

    def __repr__(self):
        return '<Subscribe {} <<-->> {} >'.format(self.user.name, self.task.name)

class PriceLookup(db.Model):
    __tablename__ = 'price_lookup'

    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), primary_key=True)
    price = db.Column(db.Integer, db.ForeignKey('prices.id'), primary_key=True)