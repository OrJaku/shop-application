from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


from .config import app_config
db = SQLAlchemy()
login = LoginManager()


def create_app(config_shop):

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config)
    app.config.from_pyfile('config.py')

    migrate = Migrate(app, db)

    db.init_app(app)
    login.init_app(app)
    from .models import User
    login.login_message = "You must be logged in to access this page."
    login.login_view = "shop.login"
    from app import models

    from .shop import views
    app.register_blueprint(views.shop)
    return app
