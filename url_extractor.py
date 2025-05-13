import json
import os

def extract_urls_from_response(response_json):
    """
    Extract URLs from the SearchAgent's JSON response and save them to a file.
    
    Args:
        response_json (str): JSON response string from the SearchAgent
    
    Returns:
        list: List of extracted URLs
    """
    try:
        # Parse the JSON response
        data = json.loads(response_json)
        
        urls = []
        
        # Check if the response contains google_search_results
        if 'google_search_results' in data:
            for result in data['google_search_results']:
                if 'sources' in result:
                    urls.extend(result['sources'])
        
        # Also check for any URLs in the answer field (some responses might include links inline)
        if 'answer' in data and isinstance(data['answer'], str):
            import re
            # Simple regex to find URLs in text
            url_pattern = re.compile(r'https?://\S+')
            additional_urls = url_pattern.findall(data['answer'])
            urls.extend(additional_urls)
        
        # Remove duplicates while preserving order
        unique_urls = []
        for url in urls:
            if url not in unique_urls:
                unique_urls.append(url)
        
        return unique_urls
    except json.JSONDecodeError:
        print("Error: Invalid JSON response")
        return []
    except Exception as e:
        print(f"Error extracting URLs: {str(e)}")
        return []

def save_urls_to_file(urls, filename="urls_for_crawling.txt"):
    """
    Save extracted URLs to a text file.
    
    Args:
        urls (list): List of URLs to save
        filename (str): Name of the file to save URLs to
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(filename, 'w') as f:
            for url in urls:
                f.write(f"{url}\n")
        print(f"Successfully saved {len(urls)} URLs to {filename}")
        return True
    except Exception as e:
        print(f"Error saving URLs to file: {str(e)}")
        return False

def extract_and_save_urls(response_json, filename="urls_for_crawling.txt"):
    """
    Extract URLs from a SearchAgent response and save them to a file.
    
    Args:
        response_json (str): JSON response string from the SearchAgent
        filename (str): Name of the file to save URLs to
    
    Returns:
        list: List of extracted URLs
    """
    urls = extract_urls_from_response(response_json)
    if urls:
        save_urls_to_file(urls, filename)
    return urls 