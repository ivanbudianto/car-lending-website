class Config(object):
  DEBUG = False
  TESTING = False
  CSRF_ENABLED = True
  SECRET_KEY = "this-really-needs-to-be-changed"
  SQLALCHEMY_DATABASE_URI = "sqlite:///development.db"
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  MAIL_SERVER = "smtp.gmail.com"
  MAIL_PORT = 465
  MAIL_USERNAME = "intellicrop@gmail.com"
  MAIL_PASSWORD = "wcibmxmugtbcztog"
  MAIL_USE_TLS = False
  MAIL_USE_SSL = True
  CKEDITOR_SERVE_LOCAL = True

class ProductionConfig(Config):
  DEBUG = False

class StagingConfig(Config):
  DEVELOPMENT = True
  DEBUG = True

class DevelopmentConfig(Config):
  DEVELOPMENT = True
  DEBUG = True

class TestingConfig(Config):
  TESTING = True