from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from app import db, app_config, create_app

config_app = app_config['development']
app = create_app(config_app)

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == "__main__":
    manager.run()