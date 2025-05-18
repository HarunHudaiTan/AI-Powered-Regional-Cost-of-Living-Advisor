import asyncio
from crawl4ai import AsyncWebCrawler, DefaultMarkdownGenerator
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode
import json
import re
import os

async def _crawl_urls_async(urls):
    """Internal async function to crawl a list of URLs"""
    md_generator = DefaultMarkdownGenerator(
        options={
            "ignore_images": True,
            "body_width": 80,
        }
    )

    browser_config = BrowserConfig(verbose=True)
    run_config = CrawlerRunConfig(
        word_count_threshold=10,
        excluded_tags=['form', 'header'],
        exclude_external_links=True,
        exclude_all_images=True,
        exclude_external_images=True,
        markdown_generator=md_generator,
        process_iframes=False,
        remove_overlay_elements=True,
        cache_mode=CacheMode.ENABLED
    )

    markdown_contents = []

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for url in urls:
            print(f"Crawling: {url}")
            result = await crawler.arun(
                url=url,
                config=run_config
            )
            if result.success:
                print(result.markdown)
                markdown_contents.append(result.markdown)

    return markdown_contents


def crawl_urls(urls):
    """
    Crawl a list of URLs and return the markdown content.

    Args:
        urls (list): List of URLs to crawl

    Returns:
        list: List of markdown contents from the crawled URLs
    """
    return asyncio.run(_crawl_urls_async(urls))
