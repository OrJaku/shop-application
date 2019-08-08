import os
from app import db, create_app

config_shop = os.getenv('development')
app = create_app(config_shop)


with app.app_context():
    print("Dropping tables")
    db.drop_all()
    print("Creating tables")
    db.create_all()
    print('Done')
