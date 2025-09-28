# ===========================
# app/routes.py
# ===========================
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main application page"""
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "title": "Web Scraping Tool"}
    )

@router.get("/docs-page", response_class=HTMLResponse)
async def docs_page(request: Request):
    """Custom documentation page"""
    return templates.TemplateResponse(
        "docs.html",
        {"request": request, "title": "API Documentation"}
    )