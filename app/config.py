class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/shop'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = '92$$%04232jf!j343dd44434r&^8ddd)*#f3f3fdhJ32foi'


class TestingConfig(Config):
    TESTING = True


app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
