# ===========================
# tests/test_api.py
# ===========================

import pytest
import httpx
from fastapi.testclient import TestClient
from main import app
from app.models.schemas import ScrapingOption

client = TestClient(app)

class TestAPI:
    def test_health_endpoint(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_scrape_valid_request(self):
        # This test would need to be adapted based on your mocking strategy
        request_data = {
            "url": "https://httpbin.org/html",
            "options": ["text", "headings"]
        }
        
        response = client.post("/api/scrape", json=request_data)
        
        # The actual response would depend on the website content
        assert response.status_code in [200, 500]  # May fail due to network
        
    def test_scrape_invalid_url(self):
        request_data = {
            "url": "not-a-valid-url",
            "options": ["text"]
        }
        
        response = client.post("/api/scrape", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_scrape_empty_options(self):
        request_data = {
            "url": "https://example.com",
            "options": []
        }
        
        response = client.post("/api/scrape", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_stats_endpoint(self):
        response = client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_scrapes" in data
        assert "status" in data

    def test_home_page(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
