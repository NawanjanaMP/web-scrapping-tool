# ===========================
# app/api/routes.py
# ===========================
from flask import Blueprint, request, jsonify, current_app, send_file
from app.core.scraper import WebScraper
from app.core.exceptions import *
from app.utils.file_handler import FileHandler
import logging
import tempfile
import json
import os

api = Blueprint('api', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)

@api.route('/scrape', methods=['POST'])
def scrape_website():
    """Scrape a website and return JSON data"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        url = data.get('url')
        options = data.get('options', [])
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        if not options:
            return jsonify({'error': 'At least one option must be selected'}), 400
        
        # Create scraper instance
        scraper = WebScraper(
            timeout=current_app.config.get('REQUEST_TIMEOUT', 30),
            max_retries=current_app.config.get('MAX_RETRIES', 3)
        )
        
        # Perform scraping
        result = scraper.scrape(url, options)
        
        # Save result if successful
        if result['success']:
            try:
                FileHandler.save_json(result)
            except Exception as e:
                logger.warning(f"Failed to save result: {e}")
        
        return jsonify(result)
        
    except InvalidURLError as e:
        return jsonify({'error': f'Invalid URL: {str(e)}'}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error in scrape_website: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/download', methods=['POST'])
def download_json():
    """Download scraped data as JSON file"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            temp_path = f.name
        
        # Generate filename
        timestamp = data.get('timestamp', '').replace(':', '-').replace('.', '-')
        filename = f"scraped_data_{timestamp}.json"
        
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error in download_json: {e}")
        return jsonify({'error': 'Failed to generate download'}), 500

@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })