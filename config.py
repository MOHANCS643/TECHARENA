import os


class Config:

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    SECRET_KEY = "TechArena@2026#SecretKey"

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL",
    "sqlite:///" + os.path.join(BASE_DIR, "techarena.db")
     )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_PERMANENT = False

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024