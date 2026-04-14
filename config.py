"""
config.py — Central configuration loader for MedPredict AI.
Reads all settings from the .env file in the project root.
"""
import os
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()

# ─── MySQL Database Config ────────────────────────────────────────────────────
DB_CONFIG = {
    "host":         os.getenv("DB_HOST",     "localhost"),
    "port":         int(os.getenv("DB_PORT", 3306)),
    "user":         os.getenv("DB_USER",     "root"),
    "password":     os.getenv("DB_PASSWORD", "chaitanya@2003"),
    "database":     os.getenv("DB_NAME",     "disease_prediction"),
    "auth_plugin":  "mysql_native_password"  # Added to bypass caching_sha2_password error
}

# ─── Google Gemini API ────────────────────────────────────────────────────────
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

# ─── App Meta ─────────────────────────────────────────────────────────────────
APP_TITLE       = "MedPredict AI"
APP_SUBTITLE    = "Disease Prediction System"
APP_VERSION     = "1.0.0"
PROJECT_LABEL   = "Final Year College Project"