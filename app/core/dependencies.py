from app.services.scraper import ScraperService

_scraper_service = None

def get_scraper_service() -> ScraperService:
    """
    Get or create a ScraperService instance.
    Uses singleton pattern to avoid creating multiple instances.
    """
    global _scraper_service
    if _scraper_service is None:
        _scraper_service = ScraperService()
    return _scraper_service 