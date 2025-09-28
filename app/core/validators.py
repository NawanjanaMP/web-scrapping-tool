# ===========================
# app/core/validators.py
# ===========================
from urllib.parse import urlparse
from typing import List
from app.core.exceptions import InvalidURLException
from app.models.schemas import ScrapingOption

class URLValidator:
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Validate if URL is properly formatted"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL and raise exception if invalid"""
        if not url:
            raise InvalidURLException("URL cannot be empty")
        
        if len(url) > 2048:
            raise InvalidURLException("URL too long")
        
        if not URLValidator.is_valid_url(url):
            raise InvalidURLException("Invalid URL format")
        
        parsed = urlparse(url)
        if parsed.scheme not in ['http', 'https']:
            raise InvalidURLException("Only HTTP and HTTPS URLs are allowed")
        
        return True

class OptionsValidator:
    @staticmethod
    def validate_options(options: List[ScrapingOption]) -> bool:
        """Validate scraping options"""
        if not options:
            raise ValueError("At least one option must be selected")
        return True