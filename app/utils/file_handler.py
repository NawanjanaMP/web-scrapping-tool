# ===========================
# app/utils/file_handler.py
# ===========================
import json
import os
from datetime import datetime
from flask import current_app

class FileHandler:
    @staticmethod
    def save_json(data, filename=None):
        """Save data as JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scraped_data_{timestamp}.json"
        
        filepath = os.path.join(current_app.config['SCRAPED_DIR'], filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    @staticmethod
    def load_json(filepath):
        """Load JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)