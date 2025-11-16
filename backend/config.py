import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "your_secret_key_here_change_in_production"
    JWT_SECRET_KEY = "jwt_secret_key_here_change_in_production"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)