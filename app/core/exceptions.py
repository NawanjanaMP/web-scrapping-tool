# ===========================
# app/core/exceptions.py
# ===========================
from fastapi import HTTPException
from typing import Any, Dict, Optional

class ScrapingException(Exception):
    """Base exception for scraping errors"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class InvalidURLException(ScrapingException):
    """Raised when URL is invalid"""
    def __init__(self, message: str = "Invalid URL format"):
        super().__init__(message, 400)

class RequestException(ScrapingException):
    """Raised when HTTP request fails"""
    def __init__(self, message: str = "Request failed"):
        super().__init__(message, 500)

class ParseException(ScrapingException):
    """Raised when parsing fails"""
    def __init__(self, message: str = "Failed to parse content"):
        super().__init__(message, 500)

class TimeoutException(ScrapingException):
    """Raised when request times out"""
    def __init__(self, message: str = "Request timed out"):
        super().__init__(message, 408)

def create_http_exception(exc: ScrapingException) -> HTTPException:
    """Convert custom exception to HTTPException"""
    return HTTPException(
        status_code=exc.status_code,
        detail=exc.message
    )
