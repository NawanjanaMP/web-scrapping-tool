# ===========================
# app/core/validators.py
# ===========================
import re
from urllib.parse import urlparse
from app.core.exceptions import InvalidURLError

class URLValidator:
    @staticmethod
    def is_valid_url(url):
        """Validate if URL is properly formatted"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def validate_url(url):
        """Validate URL and raise exception if invalid"""
        if not url:
            raise InvalidURLError("URL cannot be empty")
        
        if len(url) > 2048:
            raise InvalidURLError("URL too long")
        
        if not URLValidator.is_valid_url(url):
            raise InvalidURLError("Invalid URL format")
        
        parsed = urlparse(url)
        if parsed.scheme not in ['http', 'https']:
            raise InvalidURLError("Only HTTP and HTTPS URLs are allowed")
        
        return True

class OptionsValidator:
    VALID_OPTIONS = ['text', 'links', 'images', 'headings', 'meta', 'forms']
    
    @staticmethod
    def validate_options(options):
        """Validate scraping options"""
        if not options:
            raise ValueError("At least one option must be selected")
        
        invalid_options = set(options) - set(OptionsValidator.VALID_OPTIONS)
        if invalid_options:
            raise ValueError(f"Invalid options: {invalid_options}")
        
        return True