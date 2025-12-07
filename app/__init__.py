# third-party imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_ckeditor import CKEditor

# local imports
from .config import DevelopmentConfig


db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()
csrf = CSRFProtect()
ckeditor = CKEditor()
login_manager = LoginManager()
login_manager.login_view = "control_panel_app.login"
login_manager.login_message = "Silakan masuk untuk mengakses halaman ini."
login_manager.login_message_category = "info"

def create_app(config=DevelopmentConfig):
  app = Flask(__name__)
  app.config.from_object(config)

  db.init_app(app)
  bcrypt.init_app(app)
  mail.init_app(app)
  csrf.init_app(app)
  ckeditor.init_app(app)
  login_manager.init_app(app)

  from .views import control_panel_app, public_app
  app.register_blueprint(control_panel_app)
  app.register_blueprint(public_app)

  return app