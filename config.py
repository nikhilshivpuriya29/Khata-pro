import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Toggle: "local" for SQLite, "cloud" for PostgreSQL
MODE = os.environ.get("KHATA_MODE", "local")


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "khata-pro-secret-key-change-in-production")
    WTF_CSRF_ENABLED = True

    if MODE == "cloud":
        SQLALCHEMY_DATABASE_URI = os.environ.get(
            "DATABASE_URL", "postgresql://user:pass@localhost:5432/khata"
        )
    else:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'khata.db')}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    INTEREST_RATE = 0.02  # 2% per month
