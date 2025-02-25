#!/usr/bin/env python3
import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url="https://example.com")
            
            if hasattr(result, 'markdown'):
                print("Markdown:", result.markdown[:100])
            else:
                print("No markdown attribute found.")
                
            print("Result attributes:", [attr for attr in dir(result) if not attr.startswith('_')])
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 