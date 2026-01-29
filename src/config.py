"""
Configuration module for SOR Automation System
Loads environment variables and provides configuration settings
"""
from pathlib import Path
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# PDF Output Directory
PDF_OUTPUT_DIR = Path.home() / "Downloads" / "MindWorx_SOR_PDFs"
PDF_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def get_pdf_output_path():
    """Generate a new PDF output path with current timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return PDF_OUTPUT_DIR / f"MindWorx_Statement_of_Results_{timestamp}.pdf"

# For backward compatibility
PDF_OUTPUT = get_pdf_output_path()

class Config:
    # Database
    DB_HOST = os.getenv("DB_HOST")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    DB_PORT = int(os.getenv("DB_PORT", 3306))

    # Moodle
    MOODLE_URL = os.getenv("MOODLE_URL")
    MOODLE_TOKEN = os.getenv("MOODLE_TOKEN")

    # Dropbox Sign
    DROPBOX_SIGN_API_KEY = os.getenv("DROPBOX_SIGN_API_KEY")

    # Workflow Options
    SKIP_SIGNATURE = os.getenv("SKIP_SIGNATURE", "false").lower() == "true"

    # Test settings
    TEST_LEARNER_NAME = "SOR POD Internal POD"
    MAX_SIGNATURE_WAIT_MINUTES = 60
    SIGNATURE_CHECK_INTERVAL_SECONDS = 30
    MAX_DOWNLOAD_RETRIES = 5
    DOWNLOAD_RETRY_DELAY_SECONDS = 10
    ASSIGNMENT_COURSEMODULE_ID = 213

    # Image paths (update if needed)
    LOGO_PATH = os.getenv('LOGO_PATH', '') or None
    STAMP_PATH = os.getenv('STAMP_PATH', '') or None
    COVER_PATH = os.getenv('COVER_PATH', '') or None

    # Qualification constants
    QUAL_TITLE = "Occupational Certificate: Software Engineer"
    SAQA_ID = "119458"
    NQF_LEVEL = "NQF Level 6"
    TOTAL_CREDITS = "240 Credits"

    # Quiz weights and credits
    QUIZ_WEIGHTS = {
        12: 0.60, 13: 0.15, 14: 0.15, 15: 0.10,
        16: 0.10, 17: 0.50, 18: 0.30, 19: 0.10,
        20: 0.20, 21: 0.20, 22: 0.60, 23: 1.00
    }
    QUIZ_CREDITS = {12: 20, 13: 20, 14: 20, 15: 20, 16: 20, 17: 20, 18: 20, 19: 20, 20: 15, 21: 15, 22: 15, 23: 5}

    # Image validation placeholders
    LOGO_PATH_VALID = None
    STAMP_PATH_VALID = None
    COVER_PATH_VALID = None

    @staticmethod
    def validate_config():
        required = [Config.DB_HOST, Config.DB_USER, Config.DB_PASSWORD, Config.DB_NAME, Config.MOODLE_URL, Config.MOODLE_TOKEN, Config.DROPBOX_SIGN_API_KEY]
        if not all(required):
            print("[X] Missing required environment variables in .env")
            return False
        print("[OK] Config validated")
        return True

# Create config instance
config = Config()