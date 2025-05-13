# URL Extractor for SearchAgent

This utility extracts URLs from SearchAgent JSON responses and saves them to a file for crawling.

## Features

- Automatically extracts URLs from SearchAgent responses
- Saves URLs to a text file (one URL per line)
- Handles both URLs in the `sources` field and URLs embedded in the answer text
- Removes duplicate URLs
- Can be used both automatically (integrated with SearchAgent) or manually (standalone script)
- Integrates with the crawler for automated web crawling

## Usage

### Automatic URL Extraction

The URL extraction is now integrated with the SearchAgent. Every time a search is performed, the URLs from the response will be automatically extracted and saved to a file named `urls_for_crawling.txt`.

### Manual URL Extraction

You can also manually extract URLs from saved JSON responses using the `extract_urls.py` script:

```bash
python extract_urls.py response.json
```

Optional arguments:
- `-o, --output`: Specify output file name (default: urls_for_crawling.txt)

Example:
```bash
python extract_urls.py response.json -o my_urls.txt
```

### Crawling Extracted URLs

The `Crawl.py` script reads URLs from the `urls_for_crawling.txt` file:

```bash
python RealEstateCrawl.py
```

The crawler strictly requires URLs to be present in the specified file and will exit with an error message if:
- The URL file doesn't exist
- The URL file is empty

Optional arguments:
- `-u, --url-file`: Specify a custom URL file path (default: urls_for_crawling.txt)
- `-o, --output`: Specify output file for crawl results (default: temp_crawl_result.md)

Example:
```bash
python RealEstateCrawl.py --url-file my_urls.txt --output my_crawl_results.md
```

## Programmatic Usage

You can also use the URL extraction functions in your own code:

```python
from url_extractor import extract_and_save_urls

# Extract URLs from a JSON response string and save to a file
extract_and_save_urls(json_response, "output_file.txt")

# If you only want to extract URLs without saving to a file
from url_extractor import extract_urls_from_response
urls = extract_urls_from_response(json_response)
```

## File Format

The output file contains one URL per line, making it easy to parse for crawling:

```
https://example.com/page1
https://example.com/page2
https://another-site.com/article
```

## Complete Workflow

1. Use SearchAgent to perform searches (URLs automatically extracted to `urls_for_crawling.txt`)
2. Run the crawler to fetch content from these URLs: `python Crawl.py`
3. Process the crawled content in `temp_crawl_result.md` 