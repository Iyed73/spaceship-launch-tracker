import os
from dotenv import load_dotenv


load_dotenv()


class Config:
    SECRET_KEY = os.environ['SECRET_KEY']
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
