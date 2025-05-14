import asyncio, json
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode
import os
import argparse
import sys
from urllib.parse import urlparse

# Default allowed domains
DEFAULT_ALLOWED_DOMAINS = [
    "hepsiemlak.com",
    "emlakjet.com",
    "emlakgo.com"
]

async def main(url_file="urls_for_crawling.txt", output_file="temp_crawl_result.md", allowed_domains=None):
    # Read URLs from the specified file
    urls = []
    filtered_urls = []
    try:
        if os.path.exists(url_file):
            with open(url_file, "r") as f:
                urls = [line.strip() for line in f if line.strip()]
            
            if not urls:
                print(f"Error: No URLs found in {url_file}")
                return
            
            # Filter URLs by domain
            # Use provided domains from command line if specified,
            # otherwise use the default list
            if allowed_domains:
                allowed_domains_list = [d.strip() for d in allowed_domains.split(',')]
            else:
                allowed_domains_list = DEFAULT_ALLOWED_DOMAINS
                
            print(f"Filtering URLs by allowed domains: {allowed_domains_list}")
            
            for url in urls:
                try:
                    domain = urlparse(url).netloc
                    if any(domain.endswith(d) or domain == d for d in allowed_domains_list):
                        filtered_urls.append(url)
                    else:
                        print(f"Skipping URL with non-allowed domain: {url}")
                except Exception as e:
                    print(f"Error parsing URL {url}: {str(e)}")
            
            urls = filtered_urls
            print(f"After filtering: {len(urls)} URLs remain")
            
            if not urls:
                print("No URLs left after domain filtering. Exiting.")
                return
        else:
            print(f"Error: File {url_file} not found")
            return
    except Exception as e:
        print(f"Error reading URLs file: {str(e)}")
        return
    
    print(f"Crawling {len(urls)} URLs: {urls}")

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
        with open(output_file, "w", encoding="utf-8") as f:  # Changed mode to "w" to overwrite on each run.  Use "a" to append.

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
    parser = argparse.ArgumentParser(description="Web crawler that reads URLs from a file")
    parser.add_argument("-u", "--url-file", default="urls_for_crawling.txt", 
                        help="Path to file containing URLs to crawl (default: urls_for_crawling.txt)")
    parser.add_argument("-o", "--output", default="temp_crawl_result.md",
                        help="Path to save crawl results (default: temp_crawl_result.md)")
    parser.add_argument("-d", "--domains", 
                        help="Comma-separated list of allowed domains (e.g., 'example.com,test.org')")
    args = parser.parse_args()
    
    asyncio.run(main(args.url_file, args.output, args.domains))