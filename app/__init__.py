from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config
import os

db = SQLAlchemy()
login = LoginManager()
login.login_view = 'auth.login'
csrf = CSRFProtect()


def create_app(config_class=Config):
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    app = Flask(__name__, template_folder=os.path.join(basedir, 'templates'),
                static_folder=os.path.join(basedir, 'static'))
    app.config.from_object(config_class)

    db.init_app(app)
    login.init_app(app)
    csrf.init_app(app)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.profile import bp as profile_bp
    app.register_blueprint(profile_bp, url_prefix='/profile')

    return app

from app import models
from app.models import User


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
