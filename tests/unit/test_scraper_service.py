import pytest
from app.services.scraper import ScraperService, ScrapeOptions, ScrapedData, ScrapedMetadata, ActionResult
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
import types

@pytest.fixture
def mock_crawler():
    """Create a mock crawler for testing"""
    return MagicMock()

@pytest.fixture
def mock_scraper_service(mock_crawler):
    """Create a mock scraper service for testing"""
    service = ScraperService()
    service.crawler = mock_crawler
    return service

@pytest.mark.unit
class TestScraperService:
    """Unit tests for the ScraperService class"""

    @pytest.mark.asyncio
    async def test_scrape_url_markdown(self, mock_scraper_service, mock_crawler):
        """Test scraping a URL with markdown format"""
        # Setup mock response
        mock_result = MagicMock()
        mock_result.url = "https://example.com"
        mock_result.status_code = 200
        mock_result.metadata = {
            "title": "Example Domain",
            "description": "Example description",
            "language": "en",
            "keywords": ["example", "domain"],
            "robots": "index, follow",
            "og:title": "Example OG Title",
            "og:description": "Example OG Description",
            "og:url": "https://example.com",
            "og:image": "https://example.com/image.jpg",
            "og:site_name": "Example Site"
        }
        mock_result.to_markdown.return_value = "# Example Domain\n\nThis is an example page."
        mock_result.content = "<html><body><h1>Example Domain</h1><p>This is an example page.</p></body></html>"
        mock_result.raw_content = "<html><body><h1>Example Domain</h1><p>This is an example page.</p></body></html>"
        mock_result.links = ["https://example.com/page1", "https://example.com/page2"]
        
        # Configure mock crawler to return a coroutine
        async def mock_arun(*args, **kwargs):
            return mock_result
        mock_crawler.arun = mock_arun
        
        # Create a ScrapedData object to return from _process_formats
        scraped_data = ScrapedData(
            markdown="# Example Domain\n\nThis is an example page.",
            metadata=ScrapedMetadata(
                title="Example Domain",
                description="Example description",
                source_url="https://example.com",
                status_code=200
            )
        )
        
        # Configure _process_formats to be awaitable and return the ScrapedData
        async def mock_process_formats(*args, **kwargs):
            return scraped_data
        mock_scraper_service._process_formats = mock_process_formats
        
        # Call the service
        options = ScrapeOptions(formats=["markdown"])
        result = await mock_scraper_service.scrape_url("https://example.com", options)
        
        # Assertions
        assert result["success"] is True
        assert "data" in result
        assert result["data"].markdown == "# Example Domain\n\nThis is an example page."
        assert result["data"].metadata.title == "Example Domain"
        
    @pytest.mark.asyncio
    async def test_scrape_url_multiple_formats(self, mock_scraper_service, mock_crawler):
        """Test scraping a URL with multiple formats"""
        # Setup mock response
        mock_result = MagicMock()
        mock_result.url = "https://example.com"
        mock_result.status_code = 200
        mock_result.metadata = {"title": "Example Domain"}
        mock_result.to_markdown.return_value = "# Example Domain"
        mock_result.content = "<html><body><h1>Example Domain</h1></body></html>"
        mock_result.raw_content = "<html><body><h1>Example Domain</h1></body></html>"
        mock_result.links = ["https://example.com/page1"]
        
        # Configure mock crawler to return a coroutine
        async def mock_arun(*args, **kwargs):
            return mock_result
        mock_crawler.arun = mock_arun
        
        # Create a ScrapedData object to return from _process_formats
        scraped_data = ScrapedData(
            markdown="# Example Domain",
            html="<html><body><h1>Example Domain</h1></body></html>",
            raw_html="<html><body><h1>Example Domain</h1></body></html>",
            links=["https://example.com/page1"],
            metadata=ScrapedMetadata(
                title="Example Domain",
                source_url="https://example.com",
                status_code=200
            )
        )
        
        # Configure _process_formats to be awaitable and return the ScrapedData
        async def mock_process_formats(*args, **kwargs):
            return scraped_data
        mock_scraper_service._process_formats = mock_process_formats
        
        # Call the service
        options = ScrapeOptions(formats=["markdown", "html", "rawHtml", "links"])
        result = await mock_scraper_service.scrape_url("https://example.com", options)
        
        # Assertions
        assert result["success"] is True
        assert "data" in result
        assert result["data"].markdown == "# Example Domain"
        assert result["data"].html == "<html><body><h1>Example Domain</h1></body></html>"
        assert result["data"].links == ["https://example.com/page1"]
        
    @pytest.mark.asyncio
    async def test_scrape_url_with_json_extraction(self, mock_scraper_service, mock_crawler):
        """Test scraping a URL with JSON extraction"""
        # Setup mock response
        mock_result = MagicMock()
        mock_result.url = "https://example.com"
        mock_result.status_code = 200
        mock_result.metadata = {"title": "Example Domain"}
        mock_result.content = "<html><body><h1>Example Domain</h1></body></html>"
        
        # Configure mock crawler to return a coroutine
        async def mock_arun(*args, **kwargs):
            return mock_result
        mock_crawler.arun = mock_arun
        
        # Configure extract_structured to be awaitable
        async def mock_extract_structured(*args, **kwargs):
            return {"title": "Example Domain", "content": "This is the content"}
        mock_crawler.extract_structured = mock_extract_structured
        
        # Create a ScrapedData object to return from _process_formats
        scraped_data = ScrapedData(
            json={"title": "Example Domain", "content": "This is the content"},
            metadata=ScrapedMetadata(
                title="Example Domain",
                source_url="https://example.com",
                status_code=200
            )
        )
        
        # Configure _process_formats to be awaitable and return the ScrapedData
        async def mock_process_formats(*args, **kwargs):
            return scraped_data
        mock_scraper_service._process_formats = mock_process_formats
        
        # Call the service
        options = ScrapeOptions(
            formats=["json"],
            json_options={"schema": {"title": "string", "content": "string"}}
        )
        result = await mock_scraper_service.scrape_url("https://example.com", options)
        
        # Assertions
        assert result["success"] is True
        assert "data" in result
        assert result["data"].json == {"title": "Example Domain", "content": "This is the content"}
        
    @pytest.mark.asyncio
    async def test_scrape_url_with_actions(self, mock_scraper_service, mock_crawler):
        """Test scraping a URL with page actions"""
        # Setup mock response
        mock_result = MagicMock()
        mock_result.url = "https://example.com"
        mock_result.status_code = 200
        mock_result.metadata = {"title": "Example Domain"}
        mock_result.content = "<html><body><h1>Example Domain</h1></body></html>"
        
        # Setup mock page
        mock_page = MagicMock()
        mock_page.url = "https://example.com"
        mock_page.content.return_value = "<html><body><h1>Example After Action</h1></body></html>"
        mock_page.screenshot.return_value = b"screenshot_bytes"
        
        # Configure mock crawler to return a coroutine
        async def mock_arun(*args, **kwargs):
            return mock_result
        mock_crawler.arun = mock_arun
        
        # Configure get_page to be awaitable
        async def mock_get_page(*args, **kwargs):
            return mock_page
        mock_crawler.get_page = mock_get_page
        
        # Configure page.content to be awaitable
        async def mock_content():
            return "<html><body><h1>Example After Action</h1></body></html>"
        mock_page.content = mock_content
        
        # Configure page.screenshot to be awaitable
        async def mock_screenshot(*args, **kwargs):
            return b"screenshot_bytes"
        mock_page.screenshot = mock_screenshot
        
        # Configure page.close to be awaitable
        async def mock_close():
            return None
        mock_page.close = mock_close
        
        # Create action results
        action_results = ActionResult(
            screenshots=["base64_encoded_screenshot"],
            scrapes=[
                {
                    "url": "https://example.com",
                    "html": "<html><body><h1>Example After Action</h1></body></html>"
                }
            ]
        )
        
        # Configure _execute_actions to be awaitable and return action results
        async def mock_execute_actions(*args, **kwargs):
            return action_results
        mock_scraper_service._execute_actions = mock_execute_actions
        
        # Create a ScrapedData object to return from _process_formats
        scraped_data = ScrapedData(
            markdown="# Example Domain",
            metadata=ScrapedMetadata(
                title="Example Domain",
                source_url="https://example.com",
                status_code=200
            ),
            actions=action_results
        )
        
        # Configure _process_formats to be awaitable and return the ScrapedData
        async def mock_process_formats(*args, **kwargs):
            return scraped_data
        mock_scraper_service._process_formats = mock_process_formats
        
        # Call the service
        options = ScrapeOptions(
            formats=["markdown"],
            actions=[
                {"type": "wait", "milliseconds": 2000},
                {"type": "click", "selector": "button"},
                {"type": "screenshot"},
                {"type": "scrape"}
            ]
        )
        result = await mock_scraper_service.scrape_url("https://example.com", options)
        
        # Assertions
        assert result["success"] is True
        assert "data" in result
        assert result["data"].actions is not None
        assert len(result["data"].actions.screenshots) > 0
        assert len(result["data"].actions.scrapes) > 0
        
    @pytest.mark.asyncio
    async def test_scrape_url_error_handling(self, mock_scraper_service, mock_crawler):
        """Test error handling in scrape_url"""
        # Configure mock crawler to raise an exception
        async def mock_arun(*args, **kwargs):
            raise Exception("Connection error")
        mock_crawler.arun = mock_arun
        
        # Call the service
        result = await mock_scraper_service.scrape_url("https://example.com")
        
        # Assertions
        assert result["success"] is False
        assert "error" in result
        assert "Connection error" in result["error"] 