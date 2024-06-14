import os
from flask import Flask, render_template
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
bootstrap = Bootstrap5()
csrf = CSRFProtect()
limiter = Limiter(
    get_remote_address,
    default_limits=["300 per day", "50 per hour"],
)
mail = Mail()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    mail.init_app(app)

    from app.routes import authentication, main

    app.register_blueprint(authentication.bp, url_prefix='/authentication')
    app.register_blueprint(main.bp)

    return app


app = create_app()
