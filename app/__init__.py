import rq
from apscheduler.schedulers.blocking import BlockingScheduler
from flask import Flask
from flask_apscheduler import APScheduler
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from redis import Redis

from app.rate_limiting.limiter import RateLimiter
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
bootstrap = Bootstrap5()
limiter = RateLimiter()
mail = Mail()
moment = Moment()
scheduler = APScheduler(BlockingScheduler())
task_queue: rq.Queue | None = None


def create_app(config: type[Config]) -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(config)

    login.login_view = "authentication.login"
    login.login_message_category = "danger"

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    scheduler.init_app(app)

    app.config["BOOTSTRAP_BOOTSWATCH_THEME"] = "Litera"

    app.redis = Redis.from_url(app.config["REDIS_URL"])
    limiter.init_app(app)
    global task_queue
    task_queue = rq.Queue(connection=app.redis)
    app.task_queue = task_queue
    app.scheduler = scheduler

    from app.routes import authentication, launches, main, mission_control, subscription

    app.register_blueprint(authentication.bp, url_prefix="/authentication")
    app.register_blueprint(main.bp)
    app.register_blueprint(launches.bp)
    app.register_blueprint(subscription.bp, url_prefix="/subscription")
    app.register_blueprint(mission_control.bp)

    from app.commands.scheduler import run_scheduler
    from app.commands.seed import seed
    from app.commands.worker import run_worker

    app.cli.add_command(seed)
    app.cli.add_command(run_scheduler)
    app.cli.add_command(run_worker)

    return app
