
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

async def crawl_urls(input_urls):
    browser_conf = BrowserConfig(headless=True)  # or False to see the browser
    run_conf = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS
    )

    # Create a list to hold the results
    results = []
    # Iterate over the input URLS with async web crawler
    for input_url in input_urls:
        async with AsyncWebCrawler(config=browser_conf) as crawler:
            result = await crawler.arun(
                url=input_url,
                config=run_conf
            )
            results.append(result.markdown)
    return results
