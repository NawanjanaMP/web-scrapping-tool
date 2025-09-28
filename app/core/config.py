# ===========================
# app/core/config.py
# ===========================
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # App settings
    app_name: str = "Web Scraping Tool"
    environment: str = "development"
    secret_key: str = "dev-secret-key-change-in-production"
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Scraping settings
    request_timeout: int = 30
    max_retries: int = 3
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    
    # Rate limiting
    rate_limit_per_minute: int = 60
    
    # Security
    max_url_length: int = 2048
    allowed_schemes: List[str] = ["http", "https"]
    
    # File storage
    data_dir: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    scraped_dir: str = os.path.join(data_dir, "scraped")
    logs_dir: str = os.path.join(data_dir, "logs")
    cache_dir: str = os.path.join(data_dir, "cache")
    
    class Config:
        env_file = ".env"

settings = Settings()