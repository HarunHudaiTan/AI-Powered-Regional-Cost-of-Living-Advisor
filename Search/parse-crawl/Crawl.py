import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode

async def main():
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

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url="https://www.basarisiralamalari.com/sanko-universitesi-egitim-ucretleri-2024-ve-burslari/",
            config=run_config
        )

        if result.success:
            # Print clean content
            # First 500 chars

            # from University_fee_parser import parse_university_fees,save_to_json
            # data=parse_university_fees(result.markdown)
            # save_to_json(data,"university_fees.json")

            # with open("temp_crawl_result2.html", "w") as f:
            #     f.write(result.cleaned_html)
            #     # process_with_docling("temp_crawl_result.md")

            for image in result.media["images"]:
                print(f"Found image: {image['src']}")

            # Process links
            for link in result.links["internal"]:
                print(f"Internal link: {link['href']}")

        else:
            print(f"Crawl failed: {result.error_message}")


# from docling.document_converter import DocumentConverter

# def process_with_docling(file_path):
#     converter = DocumentConverter()
#     result = converter.convert(file_path)
#     print(result.document.export_to_dict())  # output: "### Docling Technical Report[...]"






if __name__ == "__main__":
    asyncio.run(main())
