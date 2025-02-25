#!/usr/bin/env python3
import asyncio
import sys
from playwright.async_api import async_playwright
from crawl4ai import AsyncWebCrawler

async def test_playwright_directly():
    print("Testing Playwright directly...")
    try:
        async with async_playwright() as p:
            browser_type = p.chromium
            browser = await browser_type.launch()
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto("https://example.com")
            content = await page.content()
            print(f"Direct Playwright page content length: {len(content)}")
            await browser.close()
            return True
    except Exception as e:
        print(f"Playwright direct test failed: {str(e)}")
        return False

async def test_crawl4ai():
    print("Testing Crawl4AI...")
    try:
        async with AsyncWebCrawler() as crawler:
            print("AsyncWebCrawler initialized")
            print("crawler attributes:", dir(crawler))
            
            # Test the crawler's internal components
            if hasattr(crawler, "_crawler_strategy"):
                strategy = crawler._crawler_strategy
                print("Strategy attributes:", dir(strategy))
                
                # Check if browser is initialized
                if hasattr(strategy, "browser"):
                    print("Browser exists:", strategy.browser is not None)
                else:
                    print("No browser attribute found in strategy")
            
            result = await crawler.arun(url="https://example.com")
            print("Crawl result obtained")
            
            if hasattr(result, "markdown"):
                print(f"Markdown content length: {len(result.markdown)}")
            else:
                print("No markdown attribute in result")
                print("Result attributes:", dir(result))
            
            return True
    except Exception as e:
        print(f"Crawl4AI test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print(f"Python version: {sys.version}")
    
    # First test Playwright directly
    playwright_ok = await test_playwright_directly()
    print(f"Playwright direct test {'succeeded' if playwright_ok else 'failed'}\n")
    
    # Then test Crawl4AI
    crawl4ai_ok = await test_crawl4ai()
    print(f"Crawl4AI test {'succeeded' if crawl4ai_ok else 'failed'}")

if __name__ == "__main__":
    asyncio.run(main()) 