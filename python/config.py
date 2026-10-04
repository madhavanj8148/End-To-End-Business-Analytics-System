import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory Resolution
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / ".env")

# Path Configuration
RAW_DATA_DIR = BASE_DIR / "datasets" / "raw"
CLEANED_DATA_DIR = BASE_DIR / "datasets" / "cleaned"
ENGINEERED_DATA_DIR = BASE_DIR / "datasets" / "engineered"

# Ensure essential directories exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
CLEANED_DATA_DIR.mkdir(parents=True, exist_ok=True)
ENGINEERED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Database Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_NAME = os.getenv("DB_NAME", "novanest")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
