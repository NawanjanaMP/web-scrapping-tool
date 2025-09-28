# ===========================
# app/utils/setup.py
# ===========================
import os
import logging
from pathlib import Path
from app.core.config import settings

def create_directories():
    """Create necessary directories"""
    directories = [
        settings.data_dir,
        settings.scraped_dir,
        settings.logs_dir,
        settings.cache_dir
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def setup_logging():
    """Setup logging configuration"""
    log_file = os.path.join(settings.logs_dir, 'app.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )