# ===========================
# main.py
# ===========================
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.api.routes import router as api_router
from app.core.config import settings
from app.utils.setup import create_directories, setup_logging

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    create_directories()
    setup_logging()
    yield
    # Shutdown
    pass

# Create FastAPI app
app = FastAPI(
    title="Web Scraping Tool",
    description="A powerful web scraping application with modern UI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Include API routes
app.include_router(api_router, prefix="/api")

# Main routes
from app.routes import router as main_router
app.include_router(main_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENVIRONMENT") == "development"
    )