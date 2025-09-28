# ===========================
# app/models/schemas.py
# ===========================
from pydantic import BaseModel, HttpUrl, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class ScrapingOption(str, Enum):
    TEXT = "text"
    LINKS = "links"
    IMAGES = "images"
    HEADINGS = "headings"
    META = "meta"
    FORMS = "forms"

class ScrapeRequest(BaseModel):
    url: HttpUrl
    options: List[ScrapingOption] = Field(..., min_items=1)
    
    @validator('url')
    def validate_url(cls, v):
        url_str = str(v)
        if len(url_str) > 2048:
            raise ValueError("URL too long")
        return v

class LinkData(BaseModel):
    text: str
    href: str
    absolute_url: str

class ImageData(BaseModel):
    alt: str
    src: str
    absolute_url: str

class FormInputData(BaseModel):
    name: str
    type: str
    placeholder: str
    required: bool = False

class FormData(BaseModel):
    action: str
    method: str
    inputs: List[FormInputData]

class ScrapedData(BaseModel):
    text_content: Optional[List[str]] = None
    links: Optional[List[LinkData]] = None
    images: Optional[List[ImageData]] = None
    headings: Optional[Dict[str, List[str]]] = None
    meta: Optional[Dict[str, str]] = None
    forms: Optional[List[FormData]] = None

class ScrapeResponse(BaseModel):
    url: str
    timestamp: datetime
    options_used: List[ScrapingOption]
    success: bool
    error: Optional[str] = None
    data: ScrapedData
    stats: Dict[str, int] = {}

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str = "1.0.0"