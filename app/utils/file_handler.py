# ===========================
# app/utils/file_handler.py
# ===========================
import json
import aiofiles
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from app.core.config import settings

class FileHandler:
    @staticmethod
    async def save_json(data: Dict[str, Any], filename: str = None) -> str:
        """Save data as JSON file asynchronously"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scraped_data_{timestamp}.json"
        
        filepath = Path(settings.scraped_dir) / filename
        
        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data, indent=2, ensure_ascii=False, default=str))
        
        return str(filepath)
    
    @staticmethod
    async def load_json(filepath: str) -> Dict[str, Any]:
        """Load JSON file asynchronously"""
        async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
            content = await f.read()
            return json.loads(content)