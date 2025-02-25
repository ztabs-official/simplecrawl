from typing import List, Dict, Optional, Union
from pydantic import BaseModel
from crawl4ai import AsyncWebCrawler, CrawlResult
import base64
from datetime import datetime
import asyncio

class PageAction(BaseModel):
    type: str
    milliseconds: Optional[int] = None
    selector: Optional[str] = None
    text: Optional[str] = None
    key: Optional[str] = None

class ScrapedMetadata(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    language: Optional[str] = None
    keywords: Optional[List[str]] = None
    robots: Optional[str] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_url: Optional[str] = None
    og_image: Optional[str] = None
    og_locale_alternate: List[str] = []
    og_site_name: Optional[str] = None
    source_url: str
    status_code: int

class ActionResult(BaseModel):
    screenshots: List[str] = []
    scrapes: List[Dict] = []

class ScrapedData(BaseModel):
    markdown: Optional[str] = None
    html: Optional[str] = None
    raw_html: Optional[str] = None
    screenshot: Optional[str] = None
    links: Optional[List[str]] = None
    json: Optional[Dict] = None
    metadata: ScrapedMetadata
    actions: Optional[ActionResult] = None

class ScrapeOptions(BaseModel):
    formats: List[str] = ["markdown"]
    json_options: Optional[Dict] = None
    location: Optional[Dict] = None
    actions: Optional[List[PageAction]] = None

class ScraperService:
    def __init__(self):
        self.crawler = AsyncWebCrawler()

    async def scrape_url(
        self, 
        url: str, 
        options: Optional[ScrapeOptions] = None
    ) -> Dict[str, Union[bool, ScrapedData]]:
        """
        Scrape a URL with specified options.
        
        Args:
            url: The URL to scrape
            options: Scraping options including formats, json extraction, etc.
        
        Returns:
            Dictionary containing success status and scraped data
        """
        try:
            print(f"DEBUG: Starting scrape_url for {url}")
            options = options or ScrapeOptions()
            
            # Initialize crawler with options
            crawler_config = {
                "parse_javascript": True,  # For JavaScript rendered content
                "follow_redirects": True,
                "timeout": 30,
            }
            
            # Add location-based settings if specified
            if options.location:
                crawler_config.update({
                    "country": options.location.get("country", "US"),
                    "languages": options.location.get("languages", ["en-US"])
                })

            # Handle page actions if specified
            action_results = None
            if options.actions:
                print(f"DEBUG: Executing actions: {options.actions}")
                action_results = await self._execute_actions(url, options.actions)

            # Perform the crawl
            print(f"DEBUG: Running crawler with config: {crawler_config}")
            result: CrawlResult = await self.crawler.arun(
                url=url,
                **crawler_config
            )

            # Process the results based on requested formats
            print(f"DEBUG: Processing formats: {options.formats}")
            scraped_data = await self._process_formats(result, options, action_results)
            
            print(f"DEBUG: Returning success with data: {type(scraped_data)}")
            return {
                "success": True,
                "data": scraped_data
            }
            
        except Exception as e:
            print(f"DEBUG: Error in scrape_url: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _execute_actions(
        self, 
        url: str, 
        actions: List[PageAction]
    ) -> ActionResult:
        """Execute page actions before scraping"""
        result = ActionResult()
        
        try:
            # Use the crawler's arun method to get the page content
            page_result = await self.crawler.arun(url)
            
            for action in actions:
                if action.type == "wait":
                    # Simulate wait by not doing anything
                    await asyncio.sleep(action.milliseconds / 1000 if action.milliseconds else 1)
                elif action.type == "screenshot":
                    try:
                        # Take screenshot using crawler's screenshot capability
                        screenshot = await self._take_screenshot(url, full_page=False)
                        if screenshot:
                            result.screenshots.append(screenshot)
                    except Exception as e:
                        print(f"DEBUG: Screenshot action error: {str(e)}")
                elif action.type == "scrape":
                    try:
                        # Get the current page content
                        current_result = await self.crawler.arun(url)
                        if current_result and hasattr(current_result, 'content'):
                            result.scrapes.append({
                                "url": url,
                                "html": current_result.content
                            })
                        else:
                            result.scrapes.append({
                                "url": url,
                                "html": ""
                            })
                    except Exception as e:
                        print(f"DEBUG: Scrape action error: {str(e)}")
                        result.scrapes.append({
                            "url": url,
                            "html": f"Error: {str(e)}"
                        })
                else:
                    print(f"DEBUG: Unsupported action type: {action.type}")
            
            return result
        except Exception as e:
            print(f"DEBUG: Action execution error: {str(e)}")
            return result

    async def _process_formats(
        self, 
        result: CrawlResult, 
        options: ScrapeOptions,
        action_results: Optional[ActionResult] = None
    ) -> ScrapedData:
        """Process crawl results into requested formats"""
        try:
            # Safely get metadata with defaults
            metadata = {}
            if result and hasattr(result, 'metadata'):
                if result.metadata is not None:
                    metadata = result.metadata
            
            # For source_url, ensure it's a string
            source_url = ""
            if result and hasattr(result, 'url'):
                source_url = str(result.url)
            
            # For status_code, ensure it's an integer
            status_code = 500
            if result and hasattr(result, 'status_code'):
                if isinstance(result.status_code, int):
                    status_code = result.status_code
            
            data = ScrapedData(
                metadata=ScrapedMetadata(
                    source_url=source_url,
                    status_code=status_code,
                    title=metadata.get("title") if hasattr(metadata, 'get') else None,
                    description=metadata.get("description") if hasattr(metadata, 'get') else None,
                    language=metadata.get("language") if hasattr(metadata, 'get') else None,
                    keywords=metadata.get("keywords", []) if hasattr(metadata, 'get') else [],
                    robots=metadata.get("robots") if hasattr(metadata, 'get') else None,
                    og_title=metadata.get("og:title") if hasattr(metadata, 'get') else None,
                    og_description=metadata.get("og:description") if hasattr(metadata, 'get') else None,
                    og_url=metadata.get("og:url") if hasattr(metadata, 'get') else None,
                    og_image=metadata.get("og:image") if hasattr(metadata, 'get') else None,
                    og_site_name=metadata.get("og:site_name") if hasattr(metadata, 'get') else None,
                    og_locale_alternate=metadata.get("og:locale:alternate", []) if hasattr(metadata, 'get') else []
                )
            )

            # Process each requested format
            for fmt in options.formats:
                if fmt == "markdown" and result:
                    data.markdown = result.to_markdown() if hasattr(result, 'to_markdown') else None
                elif fmt == "html" and result:
                    data.html = result.content if hasattr(result, 'content') else None
                elif fmt == "rawHtml" and result:
                    data.raw_html = result.raw_content if hasattr(result, 'raw_content') else None
                elif fmt == "links" and result:
                    data.links = result.links if hasattr(result, 'links') else []
                elif fmt.startswith("screenshot"):
                    # Take screenshot if not already taken through actions
                    if not (action_results and action_results.screenshots):
                        try:
                            screenshot = await self._take_screenshot(
                                source_url,
                                full_page="@fullPage" in fmt
                            )
                            data.screenshot = screenshot
                        except Exception as e:
                            print(f"DEBUG: Screenshot error: {str(e)}")
                elif fmt == "json" and options.json_options and result:
                    try:
                        data.json = await self._extract_structured_data(
                            result,
                            options.json_options
                        )
                    except Exception as e:
                        print(f"DEBUG: JSON extraction error: {str(e)}")
                        data.json = {}

            # Add action results if any
            if action_results:
                data.actions = action_results

            return data
        except Exception as e:
            print(f"DEBUG: Error in _process_formats: {str(e)}")
            # Create a minimal valid response
            return ScrapedData(
                metadata=ScrapedMetadata(
                    source_url="",
                    status_code=500
                )
            )

    async def _take_screenshot(self, url: str, full_page: bool = False) -> str:
        """Take a screenshot of the page"""
        try:
            # Use arun to get a valid result instead of get_page
            result = await self.crawler.arun(url)
            if hasattr(result, 'screenshot'):
                screenshot = await result.screenshot(full_page=full_page)
                return base64.b64encode(screenshot).decode()
            elif hasattr(self.crawler, 'screenshot'):
                screenshot = await self.crawler.screenshot(url, full_page=full_page)
                return base64.b64encode(screenshot).decode()
            else:
                print("DEBUG: No screenshot capability found")
                return ""
        except Exception as e:
            print(f"DEBUG: Error taking screenshot: {str(e)}")
            return ""

    async def _extract_structured_data(
        self, 
        result: CrawlResult, 
        json_options: Dict
    ) -> Dict:
        """Extract structured data based on schema or prompt"""
        try:
            if not result or not hasattr(result, 'content'):
                print("DEBUG: Result has no content for structured data extraction")
                return {}

            if not json_options:
                print("DEBUG: No JSON options provided for extraction")
                return {}

            if "schema" in json_options:
                # Use schema-based extraction
                try:
                    return await self.crawler.extract_structured(
                        result.content,
                        json_options["schema"]
                    )
                except Exception as e:
                    print(f"DEBUG: Schema extraction error: {str(e)}")
                    return {}
            elif "prompt" in json_options:
                # Use prompt-based extraction
                try:
                    return await self.crawler.extract_with_prompt(
                        result.content,
                        json_options["prompt"]
                    )
                except Exception as e:
                    print(f"DEBUG: Prompt extraction error: {str(e)}")
                    return {}
            
            print("DEBUG: No recognized extraction method in json_options")
            return {}
        except Exception as e:
            print(f"DEBUG: General extraction error: {str(e)}")
            return {} 