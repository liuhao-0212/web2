import os
from dotenv import load_dotenv

load_dotenv()


def _sqlite_uri():
    base = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(base, "dev.sqlite")
    return "sqlite:///" + path.replace("\\", "/")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-change-me")
    _use_sqlite = os.getenv("USE_SQLITE", "").strip().lower() in ("1", "true", "yes")
    SQLALCHEMY_DATABASE_URI = (
        _sqlite_uri()
        if _use_sqlite
        else "mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4".format(
            user=os.getenv("MYSQL_USER", "webapp"),
            password=os.getenv("MYSQL_PASSWORD", "webapp_secret"),
            host=os.getenv("MYSQL_HOST", "127.0.0.1"),
            port=os.getenv("MYSQL_PORT", "3306"),
            database=os.getenv("MYSQL_DATABASE", "webapp_db"),
        )
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = (
        {"pool_pre_ping": True} if not _use_sqlite else {"connect_args": {"check_same_thread": False}}
    )
