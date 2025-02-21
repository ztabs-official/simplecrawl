from crawl4ai import AsyncWebCrawler
from typing import Dict

class CrawlerService:
    @staticmethod
    async def get_markdown(url: str) -> Dict[str, str]:
        try:
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(url=url)
                
                if result.success and result.markdown:
                    return {"markdown": result.markdown}
                
                return {"markdown": "No markdown content available"}

        except Exception as e:
            return {"error": f"Failed to crawl URL: {str(e)}"} 