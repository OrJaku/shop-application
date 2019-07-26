from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from .config import app_config
db = SQLAlchemy()


def create_app(config_shop):

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config['development'])
    app.config.from_pyfile('config.py')

    db.init_app(app)

    from app import models

    from .shop import shop as shop_blueprint
    app.register_blueprint(shop_blueprint)
    return app
