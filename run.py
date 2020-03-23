from app import create_app
from app import app_config
import os

config_app = app_config['development']
app = create_app(config_app)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

if __name__ == '__main__':
    app.run()
