from flask import Flask
from .config import Config
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_apscheduler import APScheduler

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
scheduler = APScheduler()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.config['SECRET_KEY'] = '114514'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    scheduler.init_app(app)

    from .model import User

    @login.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .auth import auth as authBlueprint
    app.register_blueprint(authBlueprint)

    from .main import main as mainBlueprint
    app.register_blueprint(mainBlueprint)

    return app