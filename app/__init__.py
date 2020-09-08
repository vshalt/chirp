from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from config import config
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_moment import Moment
from flask_pagedown import PageDown

db = SQLAlchemy()
mail = Mail()
migrate = Migrate()
moment = Moment()
pagedown = PageDown()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    moment.init_app(app)
    pagedown.init_app(app)

    from app.auth import auth_blueprint
    from app.main import main_blueprint

    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(main_blueprint)

    return app
