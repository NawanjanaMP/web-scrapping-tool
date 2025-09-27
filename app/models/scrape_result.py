# ===========================
# app/models/scrape_result.py
# ===========================
from datetime import datetime
from typing import Dict, List, Any, Optional

class ScrapeResult:
    def __init__(self, url: str, options: List[str], data: Dict[str, Any], 
                 success: bool = True, error: Optional[str] = None):
        self.url = url
        self.options = options
        self.data = data
        self.success = success
        self.error = error
        self.timestamp = datetime.utcnow().isoformat()
        self.stats = self._calculate_stats()
    
    def _calculate_stats(self) -> Dict[str, int]:
        """Calculate statistics from the scraped data"""
        stats = {}
        
        for key, value in self.data.items():
            if isinstance(value, list):
                stats[f"{key}_count"] = len(value)
            elif isinstance(value, dict) and key == 'headings':
                stats['total_headings'] = sum(len(v) for v in value.values() if isinstance(v, list))
        
        return stats
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'url': self.url,
            'timestamp': self.timestamp,
            'options_used': self.options,
            'success': self.success,
            'error': self.error,
            'data': self.data,
            'stats': self.stats
        }