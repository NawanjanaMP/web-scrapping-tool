# ===========================
# config.py
# ===========================
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Scraping settings
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    
    # File storage
    DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    SCRAPED_DIR = os.path.join(DATA_DIR, 'scraped')
    LOGS_DIR = os.path.join(DATA_DIR, 'logs')
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE = 60
    
    # Security
    MAX_URL_LENGTH = 2048
    ALLOWED_SCHEMES = ['http', 'https']