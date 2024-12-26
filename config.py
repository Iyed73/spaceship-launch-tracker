import os
from dotenv import load_dotenv


load_dotenv()


class Config:
    SECRET_KEY = os.environ['SECRET_KEY']
    SECURITY_PASSWORD_SALT = os.environ['SECURITY_PASSWORD_SALT']
    APP_EMAIL = os.environ['APP_EMAIL']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    MAIL_SERVER = os.environ['MAIL_SERVER']
    MAIL_PORT = os.environ['MAIL_PORT']
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ['MAIL_USERNAME']
    MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
    MAIL_DEFAULT_SENDER = os.environ['MAIL_DEFAULT_SENDER']
    SUBSCRIBERS_REMINDER_JOB_INTERVAL = 30 * 60
    LAUNCH_REMINDER_WINDOW = 2 * 60 * 60
    TASK_QUEUE_MAX_RETRIES = 3



class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ['DEV_DATABASE_URL']
    REDIS_URL = os.environ['REDIS_URL']
    SCHEDULER_API_ENABLED = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ['TEST_DATABASE_URL']
    RATELIMIT_ENABLED = True
    WTF_CSRF_ENABLED = False
    REDIS_URL = os.environ['REDIS_URL']
