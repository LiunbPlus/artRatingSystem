import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BASE_DIR / "uploads"
THUMB_DIR = UPLOAD_DIR / "thumbnails"
DB_PATH = BASE_DIR / "data.db"

APP_TITLE = '"大众创享"作品一览'
APP_VERSION = "1.0.0"
SECRET_KEY = os.environ.get(
    "APP_SECRET_KEY", "art-rating-secret-key-change-in-production"
)
CORS_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "CORS_ORIGINS",
        "http://localhost:7999,http://127.0.0.1:7999",
    ).split(",")
    if origin.strip()
]


def ensure_upload_directories() -> None:
    for directory in ("images", "videos", "objects", "thumbnails"):
        (UPLOAD_DIR / directory).mkdir(parents=True, exist_ok=True)
