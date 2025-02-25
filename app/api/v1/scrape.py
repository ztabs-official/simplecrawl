from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
from app.services.scraper import ScraperService, ScrapeOptions, PageAction

router = APIRouter(prefix="/v1", tags=["scraper"])

class ScrapeRequest(BaseModel):
    url: HttpUrl
    formats: List[str]
    json_options: Optional[Dict[str, Any]] = None
    location: Optional[Dict[str, Any]] = None
    actions: Optional[List[PageAction]] = None

    class Config:
        schema_extra = {
            "example": {
                "url": "https://example.com",
                "formats": ["markdown", "html", "screenshot@fullPage"],
                "json_options": {
                    "schema": {
                        "title": "string",
                        "content": "string"
                    }
                },
                "location": {
                    "country": "US",
                    "languages": ["en-US"]
                },
                "actions": [
                    {"type": "wait", "milliseconds": 2000},
                    {"type": "click", "selector": "button.accept-cookies"},
                    {"type": "wait", "milliseconds": 1000},
                    {"type": "screenshot"},
                    {"type": "scrape"}
                ]
            }
        }

def get_scraper_service() -> ScraperService:
    """Get an instance of the scraper service"""
    # This allows us to swap the service with a mock in tests
    from fastapi import FastAPI
    from main import app
    
    if hasattr(app, "dependency_overrides") and app.dependency_overrides.get(get_scraper_service):
        # Use the override if it exists (during testing)
        return app.dependency_overrides[get_scraper_service]()
    
    # Otherwise, return the real service
    return ScraperService()

@router.post("/scrape", summary="Scrape a URL", description="Scrape a URL and return the content in specified formats")
async def scrape_url(
    request: ScrapeRequest,
    scraper: ScraperService = Depends(get_scraper_service)
):
    """
    Scrape a URL and return the content in specified formats.
    
    Supported Formats:
    - markdown: Clean markdown content
    - html: Processed HTML content
    - rawHtml: Raw unprocessed HTML
    - links: List of all links on the page
    - json: Structured data extraction (requires json_options)
    - screenshot: Regular screenshot
    - screenshot@fullPage: Full page screenshot
    
    Page Actions:
    - wait: Wait for specified milliseconds
    - click: Click on an element using selector
    - write: Input text into a field
    - press: Press a keyboard key
    - scrape: Capture content after actions
    - screenshot: Capture screenshot after actions
    
    Location Options:
    - country: ISO 3166-1 alpha-2 country code
    - languages: List of preferred languages
    
    Returns:
        Scraped content in requested formats with metadata and action results
    """
    try:
        options = ScrapeOptions(
            formats=request.formats,
            json_options=request.json_options,
            location=request.location,
            actions=request.actions
        )
        
        result = await scraper.scrape_url(str(request.url), options)
        
        if not result:
            raise HTTPException(
                status_code=500,
                detail="Failed to get response from scraper service"
            )
            
        if isinstance(result, dict):
            if not result.get("success", False):
                error_message = result.get("error", "Unknown error")
                raise HTTPException(
                    status_code=500,
                    detail=error_message
                )
            return result
        else:
            raise HTTPException(
                status_code=500,
                detail="Invalid response format from scraper service"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        ) 