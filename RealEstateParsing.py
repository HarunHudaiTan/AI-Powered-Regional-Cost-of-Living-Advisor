import re
import json

def parse_markdown_for_prices(markdown_file):
    """
    Parses a markdown file to extract house prices (as integers) that appear before "TL".

    Args:
        markdown_file (str): Path to the markdown file.

    Returns:
        list: A list of house prices (as integers) found in the markdown.
              Returns an empty list if no prices are found.
    """

    prices = []
    try:
        with open(markdown_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
    except FileNotFoundError:
        print(f"Error: Markdown file '{markdown_file}' not found.")
        return []
    except Exception as e:
        print(f"Error reading markdown file: {e}")
        return []

    # Regex to find prices *before* "TL".  Handles optional spaces.
    price_pattern = re.compile(r'([0-9,.]+)\s*TL', re.IGNORECASE)

    matches = price_pattern.findall(markdown_content)

    for price_str in matches:
        # Clean up the price string: remove thousands separators and try to convert to integer
        price_str = price_str.replace('.', '') # Remove thousands separators that are dots
        price_str = price_str.replace(',', '.')  # replace comma for decimals
        try:
            price = int(float(price_str))  # Convert to float first, then to integer.  This handles decimals gracefully.
            prices.append(price)
        except ValueError:
            print(f"Warning: Could not convert price '{price_str}' to integer.")

    return prices

def create_rentals_json(prices, output_file="rentals.json"):
    """
    Creates a JSON file containing a list of rental prices.

    Args:
        prices (list): A list of rental prices (integers).
        output_file (str): The name of the output JSON file.
    """

    rentals_data = {"prices": prices}

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(rentals_data, f, indent=4, ensure_ascii=False)  # ensure_ascii=False for Turkish characters
        print(f"Successfully created {output_file}")
    except Exception as e:
        print(f"Error creating JSON file: {e}")


if __name__ == '__main__':
    markdown_file = "temp_crawl_result.md"  # Change this if your file has a different name/location
    prices = parse_markdown_for_prices(markdown_file)

    if prices:
        print(f"Found prices: {prices}")
        create_rentals_json(prices)
    else:
        print("No prices found in the markdown file.")