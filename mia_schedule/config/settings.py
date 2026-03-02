"""Application configuration."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
GROUPS_FILE = BASE_DIR.parent / "Get Groups" / "mia_structure.json"

APP_NAME = "SUTE Schedule"
APP_VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "3000"))

USE_CACHE = os.getenv("USE_CACHE", "True").lower() == "true"
CACHE_LIFETIME_HOURS = int(os.getenv("CACHE_LIFETIME_HOURS", "24"))
USE_SQLITE = os.getenv("USE_SQLITE", "False").lower() == "true"

RATE_LIMIT_DELAY = float(os.getenv("RATE_LIMIT_DELAY", "1.0"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = DATA_DIR / "app.log"

SUPPORTED_LANGUAGES = ["uk", "en"]
DEFAULT_LANGUAGE = "uk"

DEVELOPER_CONTACTS = {
    "github": "https://github.com/nakata27",
    "telegram": "https://t.me/nakata27"
}

DATA_DIR.mkdir(parents=True, exist_ok=True)
(DATA_DIR / "schedules").mkdir(exist_ok=True)
