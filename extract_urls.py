#!/usr/bin/env python3
import argparse
from url_extractor import extract_and_save_urls

def main():
    parser = argparse.ArgumentParser(description="Extract URLs from SearchAgent JSON responses")
    parser.add_argument(
        "input_file", 
        help="JSON file containing SearchAgent response"
    )
    parser.add_argument(
        "-o", "--output", 
        default="urls_for_crawling.txt",
        help="Output file to save URLs (default: urls_for_crawling.txt)"
    )
    args = parser.parse_args()
    
    try:
        # Read the JSON response from file
        with open(args.input_file, 'r', encoding='utf-8') as f:
            response_json = f.read()
        
        # Extract and save URLs
        urls = extract_and_save_urls(response_json, args.output)
        
        print(f"Extracted {len(urls)} URLs from {args.input_file} and saved to {args.output}")
    
    except FileNotFoundError:
        print(f"Error: File '{args.input_file}' not found")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 