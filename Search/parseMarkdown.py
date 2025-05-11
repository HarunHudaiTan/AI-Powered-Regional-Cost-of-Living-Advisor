import re
import json


def extract_property_data(markdown_content):
    # Updated pattern to capture property names/titles
    # Captures: price, property_type, title, rooms, living_rooms, size, age, district, neighborhood
    property_pattern = r'(\d{1,3}\.\d{3}) TL.*?###\s+(.*?)\s*\nKiralık (.*?)(?:\s{2,}|\n)(\d+) \+ (\d+) (\d+) m².*?(\d+) Yaşında(?:.*?)?.*?Ankara / ([^/\n]+) / ([^/\n]+?)(?: Mah\.)? *\n'

    # For newer properties with "Sıfır Bina"
    property_pattern_new = r'(\d{1,3}\.\d{3}) TL.*?###\s+(.*?)\s*\nKiralık (.*?)(?:\s{2,}|\n)(\d+) \+ (\d+) (\d+) m².*?Sıfır Bina.*?Ankara / ([^/\n]+) / ([^/\n]+?)(?: Mah\.)? *\n'

    # Combine both patterns
    properties = re.findall(property_pattern, markdown_content, re.DOTALL)
    properties_new = re.findall(property_pattern_new, markdown_content, re.DOTALL)

    # Process the results
    results = []

    # Process properties with age
    for price, title, property_type, rooms, living_rooms, size, age, district, neighborhood in properties:
        results.append({
            "title": title.strip(),
            "price": price.replace(".", "") + " TL",
            "property_type": property_type.strip(),
            "rooms": f"{rooms}+{living_rooms}",
            "size": f"{size} m²",
            "age": f"{age} Yaşında",
            "district": f"{district.strip()}/{neighborhood.strip()} Mah."
        })

    # Process new properties (Sıfır Bina)
    for price, title, property_type, rooms, living_rooms, size, district, neighborhood in properties_new:
        results.append({
            "title": title.strip(),
            "price": price.replace(".", "") + " TL",
            "property_type": property_type.strip(),
            "rooms": f"{rooms}+{living_rooms}",
            "size": f"{size} m²",
            "age": "Sıfır Bina",
            "district": f"{district.strip()}/{neighborhood.strip()} Mah."
        })

    return results


# Process the markdown content
def parse_rental_listings(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        markdown_content = file.read()

    properties = extract_property_data(markdown_content)

    # Convert to JSON
    json_data = json.dumps(properties, ensure_ascii=False, indent=2)

    return json_data


# Example usage
if __name__ == "__main__":
    file_path = "/Users/harun/Documents/GitHub/AI-Powered-Regional-Cost-of-Living-Advisor/Search/temp_crawl_result 2.md"  # Replace with your actual file path
    json_result = parse_rental_listings(file_path)

    # Save to a JSON file
    with open("ankara_rentals.json", "w", encoding="utf-8") as json_file:
        json_file.write(json_result)

    print(f"Extracted {len(json.loads(json_result))} rental properties")
    print("Data saved to ankara_rentals.json")