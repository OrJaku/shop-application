from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from .config import app_config
db = SQLAlchemy()


def create_app(config_shop):

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config)
    app.config.from_pyfile('config.py')

    db.init_app(app)

    from app import models

    from .shop import views
    app.register_blueprint(views.shop)
    return app
