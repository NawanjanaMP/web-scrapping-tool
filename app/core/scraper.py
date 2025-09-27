# ===========================
# app/core/scraper.py
# ===========================
import requests
from datetime import datetime
import time
import logging
from urllib.parse import urlparse
from app.core.parser import HTMLParser
from app.core.validators import URLValidator, OptionsValidator
from app.core.exceptions import *

logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self, timeout=30, max_retries=3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape(self, url, options):
        """Main scraping method"""
        try:
            # Validate inputs
            URLValidator.validate_url(url)
            OptionsValidator.validate_options(options)
            
            logger.info(f"Starting scrape of {url} with options: {options}")
            
            # Fetch the page
            html_content = self._fetch_page(url)
            
            # Parse the content
            parser = HTMLParser(html_content, url)
            scraped_data = self._extract_data(parser, options)
            
            # Prepare result
            result = {
                'url': url,
                'timestamp': datetime.utcnow().isoformat(),
                'options_used': options,
                'success': True,
                'data': scraped_data,
                'stats': self._calculate_stats(scraped_data)
            }
            
            logger.info(f"Successfully scraped {url}")
            return result
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return {
                'url': url,
                'timestamp': datetime.utcnow().isoformat(),
                'options_used': options,
                'success': False,
                'error': str(e),
                'data': {},
                'stats': {}
            }
    
    def _fetch_page(self, url):
        """Fetch the webpage content"""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching {url} (attempt {attempt + 1})")
                
                response = self.session.get(
                    url,
                    timeout=self.timeout,
                    allow_redirects=True
                )
                
                response.raise_for_status()
                
                # Check content type
                content_type = response.headers.get('content-type', '').lower()
                if 'text/html' not in content_type:
                    raise ParseError(f"Expected HTML content, got {content_type}")
                
                return response.text
                
            except requests.exceptions.Timeout as e:
                last_error = TimeoutError(f"Request timed out after {self.timeout} seconds")
                logger.warning(f"Timeout on attempt {attempt + 1}")
                
            except requests.exceptions.ConnectionError as e:
                last_error = RequestError(f"Connection error: {str(e)}")
                logger.warning(f"Connection error on attempt {attempt + 1}")
                
            except requests.exceptions.HTTPError as e:
                last_error = RequestError(f"HTTP error {response.status_code}: {str(e)}")
                logger.warning(f"HTTP error on attempt {attempt + 1}")
                
            except Exception as e:
                last_error = RequestError(f"Unexpected error: {str(e)}")
                logger.warning(f"Unexpected error on attempt {attempt + 1}")
            
            # Wait before retry
            if attempt < self.max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
        
        raise last_error
    
    def _extract_data(self, parser, options):
        """Extract data based on selected options"""
        data = {}
        
        extraction_methods = {
            'text': parser.extract_text_content,
            'links': parser.extract_links,
            'images': parser.extract_images,
            'headings': parser.extract_headings,
            'meta': parser.extract_meta_data,
            'forms': parser.extract_forms
        }
        
        for option in options:
            if option in extraction_methods:
                try:
                    data[f"{option}_content" if option == 'text' else option] = extraction_methods[option]()
                except Exception as e:
                    logger.error(f"Error extracting {option}: {e}")
                    data[f"{option}_content" if option == 'text' else option] = []
        
        return data
    
    def _calculate_stats(self, data):
        """Calculate statistics from scraped data"""
        stats = {}
        
        for key, value in data.items():
            if isinstance(value, list):
                stats[f"{key}_count"] = len(value)
            elif isinstance(value, dict):
                if key == 'headings':
                    stats['total_headings'] = sum(len(v) for v in value.values() if isinstance(v, list))
                else:
                    stats[f"{key}_fields"] = len(value)
        
        return stats