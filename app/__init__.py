from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail
from flask_moment import Moment
from redis import Redis
import rq
from flask_apscheduler import APScheduler


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
bootstrap = Bootstrap5()
limiter = Limiter(
    get_remote_address,
    default_limits=["500 per day", "100 per hour"],
)
mail = Mail()
moment = Moment()
scheduler = APScheduler()
task_queue = None


def create_app(config):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(config)

    login.login_view = "authentication.login"
    login.login_message_category = "danger"

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)
    limiter.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    scheduler.init_app(app)

    if not app.testing:
        scheduler.start()
        from app.scheduled_jobs.launch_reminder_job import remind_subscribers

    app.config["BOOTSTRAP_BOOTSWATCH_THEME"] = "Litera"

    app.redis = Redis.from_url(app.config["REDIS_URL"])
    global task_queue
    task_queue = rq.Queue(connection=app.redis)
    app.task_queue = task_queue
    app.scheduler = scheduler

    from app.routes import authentication, main, mission_control, launches, subscription
    app.register_blueprint(authentication.bp, url_prefix="/authentication")
    app.register_blueprint(main.bp)
    app.register_blueprint(launches.bp)
    app.register_blueprint(subscription.bp, url_prefix="/subscription")
    app.register_blueprint(mission_control.bp)

    return app
