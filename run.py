from app import create_app
from app import app_config

config_app = app_config['development']
app = create_app(config_app)


if __name__ == '__main__':
    app.run()
