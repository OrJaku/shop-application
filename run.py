import os
from app import create_app


config_shop = os.getenv('development')
app = create_app(config_shop)

if __name__ == '__main__':
    app.run()
