# ===========================
# app/core/exceptions.py
# ===========================
class ScrapingError(Exception):
    """Base exception for scraping errors"""
    pass

class InvalidURLError(ScrapingError):
    """Raised when URL is invalid"""
    pass

class RequestError(ScrapingError):
    """Raised when HTTP request fails"""
    pass

class ParseError(ScrapingError):
    """Raised when parsing fails"""
    pass

class TimeoutError(ScrapingError):
    """Raised when request times out"""
    pass