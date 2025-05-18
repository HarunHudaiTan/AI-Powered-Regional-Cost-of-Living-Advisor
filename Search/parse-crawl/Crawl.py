import asyncio
from crawl4ai import AsyncWebCrawler, DefaultMarkdownGenerator
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode
import json
import re
import os







async def main():
    md_generator = DefaultMarkdownGenerator(
        options={
            "ignore_images": True,  # This removes all image references
            # You can add other options as needed
            "body_width": 80,  # Optional: wrap text at 80 characters
            # "ignore_links": True  # Optional: also remove hyperlinks
        }
    )
    urls=""


    browser_config = BrowserConfig(verbose=True)
    run_config = CrawlerRunConfig(
        # Content filtering
        word_count_threshold=10,
        excluded_tags=['form', 'header'],
        exclude_external_links=True,
        exclude_all_images=True,
        exclude_external_images=True,
        markdown_generator=md_generator,
        # Content processing
        process_iframes=False,
        remove_overlay_elements=True,

        # Cache control
        cache_mode=CacheMode.ENABLED  # Use cache if available
    )

    # Create a directory for results if it doesn't exist
    results_dir = os.path.join(os.path.dirname(__file__), 'crawl_results')
    os.makedirs(results_dir, exist_ok=True)


    async with AsyncWebCrawler(config=browser_config) as crawler:
        for url in urls:
            print(f"Crawling: {url}")
            result = await crawler.arun(
                url=url,
                config=run_config
            )
            selected_links = []
            if result.success:
                # Create a safe filename from the URL
                # Replace special characters with underscores
                filename = re.sub(r'[^a-zA-Z0-9]', '_', url)
                # Truncate if too long

                if len(filename) > 100:
                    filename = filename[:100]

                # Save markdown content to a text file
                # markdown_with_images = result.markdown.raw_markdown
                # markdown_without_images = re.sub(r'!\[.*?\]\(.*?\)', '', markdown_with_images)
                txt_file_path = os.path.join(results_dir, f"{filename}.txt")
                with open(txt_file_path, 'w', encoding='utf-8') as f:
                    f.write(result.markdown)
                print(f"Saved markdown content to {txt_file_path}")


if __name__ == "__main__":
    asyncio.run(main())
