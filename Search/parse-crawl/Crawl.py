import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode
import json
import os
from md_parse import extract_markdown_sections_from_text

async def main():
    # Read URLs from the JSON file
    json_path = os.path.join(os.path.dirname(__file__), 'internal_links.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        urls = json.load(f)

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

    # Create a directory for results if it doesn't exist
    results_dir = os.path.join(os.path.dirname(__file__), 'crawl_results')
    os.makedirs(results_dir, exist_ok=True)

    parsed_results = {}

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for url in urls:
            print(f"Crawling: {url}")
            result = await crawler.arun(
                url=url,
                config=run_config
            )
            selected_links = []
            if result.success:
                # # Get internal links from the result
                # internal_links = result.links["internal"]
                #
                # # Print the links (from index 2 to 79)
                # print("Selected internal links:")
                # for i, link in enumerate(internal_links[2:79]):
                #     selected_links.append(link["href"])
                #
                # with open("internal_links.json", "w") as f:
                #     json.dump(selected_links, f, indent=4)


                # Create a safe filename from the URL
                filename = url.split('/')[-2] if url.split('/')[-2] else 'index'
                
                # Save markdown content to a text file
                txt_file_path = os.path.join(results_dir, f"{filename}.txt")
                with open(txt_file_path, 'w', encoding='utf-8') as f:
                    f.write(result.markdown)
                print(f"Saved markdown content to {txt_file_path}")
                
                # Directly process the markdown content without saving to file
                try:
                    # Parse the markdown content directly from the result
                    parsed_content = extract_markdown_sections_from_text(result.markdown)
                    parsed_results[filename] = parsed_content
                    print(f"Successfully parsed markdown from {url}")
                except Exception as e:
                    print(f"Error parsing markdown from {url}: {str(e)}")
            else:
                print(f"Crawl failed for {url}: {result.error_message}")

    
# from docling.document_converter import DocumentConverter

# def process_with_docling(file_path):
#     converter = DocumentConverter()
#     result = converter.convert(file_path)
#     print(result.document.export_to_dict())  # output: "### Docling Technical Report[...]"

if __name__ == "__main__":
    asyncio.run(main())
