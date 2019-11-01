from flask import Flask, flash, redirect, url_for
from .config import Config
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_apscheduler import APScheduler
from datetime import datetime

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
scheduler = APScheduler()

def clean_expired_tasks():
    for job in scheduler.get_jobs():
        id = job.id
        task = Task.query.filter_by(id=id)
        if datetime.now() > task.expiring_time:
            job.remove()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.config['SECRET_KEY'] = '114514'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    db.init_app(app)
    db.app = app
    migrate.init_app(app, db)
    login.init_app(app)
    scheduler.api_enabled = True
    scheduler.init_app(app)

    from .model import User, Task

    @login.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    @login.unauthorized_handler
    def unauthorized_callback():
        flash('Please login first.')
        return redirect(url_for('auth.login'))

    scheduler.start()
    scheduler.add_job(
        func=clean_expired_tasks,
        id='clean_expired_tasks', 
        trigger='interval', 
        minutes=60*24, 
        misfire_grace_time=60*15, 
        replace_existing=True
        )

    from .auth import auth as authBlueprint
    app.register_blueprint(authBlueprint)

    from .main import main as mainBlueprint
    app.register_blueprint(mainBlueprint)

    return app