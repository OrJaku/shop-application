from app import db, create_app
from app.userShop.models import Role, User
from app import app_config


from flask_migrate import Migrate

config_app = app_config['development']
app = create_app(config_app)


with app.app_context():
    print("\nDropping tables")
    db.drop_all()
    print("Creating tables")
    migrate = Migrate(app, db)

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
                password="admin",
                )
    admin_user.role = [admin_role]
    db.session.add(admin_user)
    db.session.commit()
    print(".. admin user has been created")
    print('\nDone')
