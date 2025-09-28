# ===========================
# app/api/routes.py
# ===========================
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from datetime import datetime
import logging
import tempfile
import json
import os

from app.models.schemas import ScrapeRequest, ScrapeResponse, HealthResponse
from app.core.scraper import WebScraper
from app.utils.file_handler import FileHandler
from app.core.exceptions import ScrapingException, create_http_exception

router = APIRouter()
logger = logging.getLogger(__name__)

# Global scraper instance
scraper = WebScraper()

@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_website(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """
    Scrape a website and return structured data
    
    - **url**: The URL to scrape
    - **options**: List of data types to extract (text, links, images, headings, meta, forms)
    """
    try:
        url_str = str(request.url)
        logger.info(f"Scraping request for: {url_str}")
        
        # Perform scraping
        result = await scraper.scrape(url_str, request.options)
        
        # Save result in background if successful
        if result.success:
            background_tasks.add_task(
                save_result_background, 
                result.dict()
            )
        
        return result
        
    except ScrapingException as e:
        logger.error(f"Scraping exception: {e.message}")
        raise create_http_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error in scrape_website: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def save_result_background(result_data: dict):
    """Background task to save scraping results"""
    try:
        await FileHandler.save_json(result_data)
        logger.info("Scraping result saved successfully")
    except Exception as e:
        logger.warning(f"Failed to save scraping result: {e}")

@router.post("/download")
async def download_json(request: dict):
    """
    Download scraped data as JSON file
    """
    try:
        if not request:
            raise HTTPException(status_code=400, detail="No data provided")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(request, f, indent=2, ensure_ascii=False, default=str)
            temp_path = f.name
        
        # Generate filename
        timestamp = request.get('timestamp', datetime.utcnow().isoformat()).replace(':', '-').replace('.', '-')
        filename = f"scraped_data_{timestamp}.json"
        
        return FileResponse(
            temp_path,
            filename=filename,
            media_type='application/json',
            background=BackgroundTasks()
        )
        
    except Exception as e:
        logger.error(f"Error in download_json: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate download")

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow()
    )

@router.get("/stats")
async def get_stats():
    """Get application statistics"""
    try:
        # Count scraped files
        from pathlib import Path
        from app.core.config import settings
        
        scraped_dir = Path(settings.scraped_dir)
        file_count = len(list(scraped_dir.glob("*.json"))) if scraped_dir.exists() else 0
        
        return {
            "total_scrapes": file_count,
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")