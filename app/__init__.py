# ===========================
# app/__init__.py
# ===========================
from flask import Flask
from flask_cors import CORS
from app.config import Config
import os
import logging

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS
    CORS(app)
    
    # Create necessary directories
    os.makedirs(app.config['SCRAPED_DIR'], exist_ok=True)
    os.makedirs(app.config['LOGS_DIR'], exist_ok=True)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(app.config['LOGS_DIR'], 'app.log')),
            logging.StreamHandler()
        ]
    )
    
    # Register blueprints
    from app.api.routes import api
    app.register_blueprint(api)
    
    # Register main routes
    from app import routes
    
    return app