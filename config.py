import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "").strip()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 300}
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    WTF_CSRF_TIME_LIMIT = 3600
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")

    @classmethod
    def validate(cls):
        if not cls.SECRET_KEY or cls.SECRET_KEY == "replace-with-a-long-random-secret":
            raise RuntimeError("Set a strong SECRET_KEY in your environment.")
        if not cls.SQLALCHEMY_DATABASE_URI:
            raise RuntimeError("Set DATABASE_URL to your Supabase PostgreSQL connection string.")
        uri = cls.SQLALCHEMY_DATABASE_URI
        if uri.startswith("postgres://"):
            cls.SQLALCHEMY_DATABASE_URI = uri.replace("postgres://", "postgresql+psycopg://", 1)
        elif uri.startswith("postgresql://"):
            cls.SQLALCHEMY_DATABASE_URI = uri.replace("postgresql://", "postgresql+psycopg://", 1)
        if os.getenv("FLASK_DEBUG", "false").lower() != "true":
            cls.SESSION_COOKIE_SECURE = True
