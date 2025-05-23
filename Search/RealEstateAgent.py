
from proj_llm_agent import LLM_Agent
import os
# Import the crawling functions from Crawl.py
from Crawl import crawl_urls


class RealEstateAgent(LLM_Agent):
    def __init__(self):
        super().__init__("Real Estate Agent", self.system_instructions, "application/json")

    system_instructions = """
# Real Estate Listing Extractor

Extract key real estate information from provided text files and output structured data for multiple listings.

## Instructions:
- Process the input text to identify individual property listings
- Extract key details for each listing: price, room configuration, size in square meters, URL link, and address
- Generate at least 10 JSON objects from the input data when available
- Format each listing into a standardized JSON structure
- All fields should be strings including numeric values
- If a field is not available in the source data, include it with an empty string value

## Output Format:
Each listing should be formatted as:
{
 "price": "price with currency",
 "room": "room configuration (e.g., 2+1, 3+1)",
 "sqmeter": "size in square meters",
 "link": "URL to the original listing",
 "address": "location/address of the property"
}

## Examples:

Example 1:
Input: "YENİ Kiralık Daire Keçiören - Kanuni MahallesiDaire | 3+1 | Kot 2 (-2). Kat | 95 m²15.000 TLTelefona Bak"
Output: 
{
 "price": "15.000 TL",
 "room": "3+1",
 "sqmeter": "95 m²",
 "link": "https://www.emlakjet.com/ilan/kiralik-daire-17355246/",
 "address": "Keçiören - Kanuni Mahallesi, Ankara"
}

Example 2:
Input: "Marka/ Referans Ankara'da Güney Batı Cephe Eşyalı Cam Balkonlu 2+1 Kiralık Daire Etimesgut - Devlet MahallesiDaire | 2+1 | 28. Kat | 90 m²37.500 TLTelefona Bak"
Output:
{
 "price": "37.500 TL",
 "room": "2+1",
 "sqmeter": "90 m²",
 "link": "https://www.emlakjet.com/ilan/marka-referans-ankara-da-guney-bati-cephe-esyali-cam-balkonlu-21-kiralik-daire-17354685/",
 "address": "Etimesgut - Devlet Mahallesi, Ankara"
}

Example 3:
Input: "YENİ Geniş Balkonlu, Sıfır, Kiralık 1+1 Daire Beypazarı - Kurtuluş MahallesiDaire | 1+1 | 2. Kat | 50 m²13.000 TLTelefona Bak"
Output:
{
 "price": "13.000 TL",
 "room": "1+1",
 "sqmeter": "50 m²",
 "link": "https://www.emlakjet.com/ilan/genis-balkonlu-sifir-kiralik-11-daire-17356872/",
 "address": "Beypazarı - Kurtuluş Mahallesi, Ankara"
}


Note: Ensure all 10+ JSON objects are correctly formatted. If there aren't enough individual listings in the input, include empty placeholder objects to reach the minimum count.
"""


real_estate_agent = RealEstateAgent()
from KeywordAgent import parse_keywords
from Search import search, parse_search_links, filter_links

# Define the path for the links file
LINKS_FILE_PATH = os.path.join(os.path.dirname(__file__), 'filtered_links.txt')


def real_estate_agent_response(prompt):
    # Get keywords and search for links
    keywords = parse_keywords(prompt)
    search_links = search(keywords)
    links = parse_search_links(search_links)
    filtered_links = filter_links(links)
    # Option 1: Crawl the URLs directly from the list
    crawled_files = crawl_urls(filtered_links)
    
    response=real_estate_agent.generate_response(prompt+"crawled_files:"f"{crawled_files}")
    return response

response=real_estate_agent_response("ankara keçiören kiralık ev fiyatları")
print(response.text)