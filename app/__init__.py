from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .config import app_config


db = SQLAlchemy()
login = LoginManager()


def create_app(config_app):

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_app)

    db.init_app(app)
    login.init_app(app)
    from .userShop.models import User
    login.login_message = "You must be logged in to access this page."
    login.login_view = "userShop.login"

    from .shop.views import shop
    from .postShop.views import postShop
    from .userShop.views import userShop, google_oauth
    app.register_blueprint(shop)
    app.register_blueprint(postShop)
    app.register_blueprint(userShop)
    app.register_blueprint(google_oauth, url_prefix='/login/google')

    return app
