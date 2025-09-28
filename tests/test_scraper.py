# ===========================
# tests/test_scraper.py
# ===========================

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from app.core.scraper import WebScraper
from app.models.schemas import ScrapingOption
from app.core.exceptions import InvalidURLException

class TestWebScraper:
    def setup_method(self):
        self.scraper = WebScraper()
    
    @pytest.mark.asyncio
    async def test_valid_scraping(self):
        html_content = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Main Title</h1>
                <p>This is test content</p>
                <a href="/test">Test Link</a>
            </body>
        </html>
        """
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.text = html_content
            mock_response.headers = {'content-type': 'text/html'}
            mock_response.raise_for_status = AsyncMock()
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await self.scraper.scrape(
                'https://example.com', 
                [ScrapingOption.TEXT, ScrapingOption.HEADINGS]
            )
            
            assert result.success is True
            assert result.data.text_content is not None
            assert result.data.headings is not None
    
    @pytest.mark.asyncio
    async def test_invalid_url(self):
        result = await self.scraper.scrape('invalid-url', [ScrapingOption.TEXT])
        assert result.success is False
        assert 'Invalid URL format' in result.error
    
    @pytest.mark.asyncio
    async def test_empty_options(self):
        result = await self.scraper.scrape('https://example.com', [])
        assert result.success is False