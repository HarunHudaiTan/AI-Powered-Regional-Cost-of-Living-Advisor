import asyncio, json
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode

async def main():

    urls = [

        "https://www.hepsiemlak.com/kecioren-kiralik",
        "https://www.emlakjet.com/kiralik-konut/ankara-kecioren"

    ]

    browser_config = BrowserConfig(verbose=True)
    run_config = CrawlerRunConfig(
        # Content filtering
        word_count_threshold=10,
        excluded_tags=['form', 'header'],
        exclude_external_links=True,

        # Content processing
        process_iframes=True,
        remove_overlay_elements=True,

        # Cache control
        cache_mode=CacheMode.ENABLED  # Use cache if available
    )

    results = []

    async with AsyncWebCrawler(config=browser_config) as crawler:
        # Open the file in append mode for writing multiple results
        with open("temp_crawl_result.md", "w", encoding="utf-8") as f:  # Changed mode to "w" to overwrite on each run.  Use "a" to append.

            for result in await crawler.arun_many(urls, config=run_config):


                if result.success:

                    # Write the markdown content for each successful crawl
                    f.write(f"# URL: {result.url}\n\n")  # Add URL as a header
                    f.write(result.markdown)
                    f.write("\n\n---\n\n")  # Add a separator between results

                # Process images
                    for image in result.media["images"]:
                        print(f"Found image: {image['src']}")

                # Process links
                    for link in result.links["internal"]:
                        print(f"Internal link: {link['href']}")

                else:
                    print(f"Crawl failed for {result.url}: {result.error_message}")


if __name__ == "__main__":
    asyncio.run(main())