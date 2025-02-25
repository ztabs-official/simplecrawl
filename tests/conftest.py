import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock, AsyncMock
from app.api.v1.scrape import get_scraper_service
from app.services.scraper import ScrapedData, ScrapedMetadata

@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app"""
    # Clear any previous dependency overrides
    app.dependency_overrides = {}
    
    with TestClient(app) as client:
        yield client
        
@pytest.fixture
def mock_scraper_service():
    """Create a mock scraper service for testing"""
    mock_service = MagicMock()
    mock_service.scrape_url = AsyncMock()
    return mock_service

@pytest.fixture
def setup_mock_dependency(mock_scraper_service):
    """Set up the mock dependency override for the scraper service"""
    app.dependency_overrides[get_scraper_service] = lambda: mock_scraper_service
    yield mock_scraper_service
    app.dependency_overrides = {}
