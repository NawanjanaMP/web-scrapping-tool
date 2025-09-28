# ===========================
# app/core/scraper.py
# ===========================
import httpx
from datetime import datetime
import asyncio
import logging
from typing import List, Dict, Any

from app.core.parser import HTMLParser
from app.core.validators import URLValidator, OptionsValidator
from app.core.exceptions import *
from app.models.schemas import ScrapingOption, ScrapeResponse, ScrapedData
from app.core.config import settings

logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self):
        self.timeout = settings.request_timeout
        self.max_retries = settings.max_retries
        
        # HTTP client configuration
        self.client_config = {
            'timeout': httpx.Timeout(self.timeout),
            'follow_redirects': True,
            'headers': {
                'User-Agent': settings.user_agent
            }
        }
    
    async def scrape(self, url: str, options: List[ScrapingOption]) -> ScrapeResponse:
        """Main scraping method"""
        start_time = datetime.utcnow()
        
        try:
            # Validate inputs
            URLValidator.validate_url(url)
            OptionsValidator.validate_options(options)
            
            logger.info(f"Starting scrape of {url} with options: {options}")
            
            # Fetch the page
            html_content = await self._fetch_page(url)
            
            # Parse the content
            parser = HTMLParser(html_content, url)
            scraped_data = await self._extract_data(parser, options)
            
            # Calculate statistics
            stats = self._calculate_stats(scraped_data)
            
            # Prepare result
            result = ScrapeResponse(
                url=url,
                timestamp=start_time,
                options_used=options,
                success=True,
                data=scraped_data,
                stats=stats
            )
            
            logger.info(f"Successfully scraped {url}")
            return result
            
        except ScrapingException as e:
            logger.error(f"Scraping error for {url}: {e.message}")
            return ScrapeResponse(
                url=url,
                timestamp=start_time,
                options_used=options,
                success=False,
                error=e.message,
                data=ScrapedData(),
                stats={}
            )
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {e}")
            return ScrapeResponse(
                url=url,
                timestamp=start_time,
                options_used=options,
                success=False,
                error=f"Unexpected error: {str(e)}",
                data=ScrapedData(),
                stats={}
            )
    
    async def _fetch_page(self, url: str) -> str:
        """Fetch the webpage content with retries"""
        last_error = None
        
        async with httpx.AsyncClient(**self.client_config) as client:
            for attempt in range(self.max_retries):
                try:
                    logger.info(f"Fetching {url} (attempt {attempt + 1})")
                    
                    response = await client.get(url)
                    response.raise_for_status()
                    
                    # Check content type
                    content_type = response.headers.get('content-type', '').lower()
                    if 'text/html' not in content_type:
                        raise ParseException(f"Expected HTML content, got {content_type}")
                    
                    return response.text
                    
                except httpx.TimeoutException:
                    last_error = TimeoutException(f"Request timed out after {self.timeout} seconds")
                    logger.warning(f"Timeout on attempt {attempt + 1}")
                    
                except httpx.ConnectError as e:
                    last_error = RequestException(f"Connection error: {str(e)}")
                    logger.warning(f"Connection error on attempt {attempt + 1}")
                    
                except httpx.HTTPStatusError as e:
                    last_error = RequestException(f"HTTP error {e.response.status_code}")
                    logger.warning(f"HTTP error on attempt {attempt + 1}")
                    
                except Exception as e:
                    last_error = RequestException(f"Unexpected error: {str(e)}")
                    logger.warning(f"Unexpected error on attempt {attempt + 1}")
                
                # Wait before retry with exponential backoff
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
        
        raise last_error
    
    async def _extract_data(self, parser: HTMLParser, options: List[ScrapingOption]) -> ScrapedData:
        """Extract data based on selected options"""
        data_dict = {}
        
        extraction_methods = {
            ScrapingOption.TEXT: parser.extract_text_content,
            ScrapingOption.LINKS: parser.extract_links,
            ScrapingOption.IMAGES: parser.extract_images,
            ScrapingOption.HEADINGS: parser.extract_headings,
            ScrapingOption.META: parser.extract_meta_data,
            ScrapingOption.FORMS: parser.extract_forms
        }
        
        # Extract data concurrently
        tasks = []
        for option in options:
            if option in extraction_methods:
                tasks.append(self._safe_extract(option, extraction_methods[option]))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, option in enumerate([opt for opt in options if opt in extraction_methods]):
            result = results[i]
            if isinstance(result, Exception):
                logger.error(f"Error extracting {option}: {result}")
                continue
            
            field_name = "text_content" if option == ScrapingOption.TEXT else option.value
            data_dict[field_name] = result
        
        return ScrapedData(**data_dict)
    
    async def _safe_extract(self, option: ScrapingOption, method):
        """Safely execute extraction method"""
        try:
            return await method()
        except Exception as e:
            logger.error(f"Error in {option} extraction: {e}")
            return [] if option in [ScrapingOption.TEXT, ScrapingOption.LINKS, 
                                   ScrapingOption.IMAGES, ScrapingOption.FORMS] else {}
    
    def _calculate_stats(self, data: ScrapedData) -> Dict[str, int]:
        """Calculate statistics from scraped data"""
        stats = {}
        
        # Convert to dict for easier processing
        data_dict = data.dict()
        
        for key, value in data_dict.items():
            if value is None:
                continue
                
            if isinstance(value, list):
                stats[f"{key}_count"] = len(value)
            elif isinstance(value, dict):
                if key == 'headings':
                    stats['total_headings'] = sum(len(v) for v in value.values() if isinstance(v, list))
                else:
                    stats[f"{key}_fields"] = len(value)
        
        return stats
