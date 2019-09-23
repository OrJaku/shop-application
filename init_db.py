import os
from app import db, create_app
from app.models import Role, User

from flask_migrate import Migrate

config_shop = os.getenv('development')
app = create_app(config_shop)


with app.app_context():
    print("\nDropping tables")
    migrate = Migrate(app, db)
    db.drop_all()
    print("Creating tables")
    db.create_all()
    print("\nImplementing data...")
    guest_role = Role(name="guest")
    db.session.add(guest_role)
    admin_role = Role(name="admin")
    db.session.add(admin_role)
    db.session.commit()
    print(".. roles have been added")
    admin_user = User(first_name='admin',
                last_name='admin',
                username='admin',
                email='admin@shop.com',
                password="admin")
    admin_user.role = [admin_role]
    db.session.add(admin_user)
    db.session.commit()
    print(".. admin user has been created")
    print('\nDone')
