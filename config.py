import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Auto-detect: Railway sets DATABASE_URL for PostgreSQL
# Falls back to SQLite for local development
DATABASE_URL = os.environ.get("DATABASE_URL", "")

# Railway uses postgres:// but SQLAlchemy needs postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "khata-pro-secret-key-change-in-production")
    WTF_CSRF_ENABLED = True

    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'khata.db')}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    INTEREST_RATE = 0.02  # 2% per month
