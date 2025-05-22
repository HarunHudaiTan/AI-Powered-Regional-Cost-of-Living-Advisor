from Agent import Agent
from proj_llm_agent import LLM_Agent
import os
# Import the crawling functions from Crawl.py
from Crawl import crawl_urls
from RAG.RealEstateRAG import retrieveDocs, show_results, create_chroma_client
from chromadb.utils import embedding_functions


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
- For tariff information:
  * Analyze the RAG results to find relevant tariff information
  * Extract and format the values into standardized formats:
    - waterTariff: Convert to "XX.XX TL/m³" format
    - naturalGasTariff: Convert to "XX.XX TL/m³" format
    - electricityTariff: Convert to "XXXX TL/kWh" format
    - internetTariff: Convert to "XXX TL" format
  * If a specific tariff is not found in RAG results, set its value to null
  * Do not add any additional information or descriptions to the tariff fields

## Output Format:
Each listing should be formatted as:
{
 "price": "price with currency",
 "room": "room configuration (e.g., 2+1, 3+1)",
 "sqmeter": "size in square meters",
 "link": "URL to the original listing",
 "address": "location/address of the property",
 "waterTariff": "XX.XX TL/m³" or null,
 "naturalGasTariff": "XX.XX TL/m³" or null,
 "electricityTariff": "XXXX TL/kWh" or null,
 "internetTariff": "XXX TL" or null
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
 "address": "Keçiören - Kanuni Mahallesi, Ankara",
 "waterTariff": "43.15 TL/m³",
 "naturalGasTariff": "8.34 TL/m³",
 "electricityTariff": "1456 TL/kWh",
 "internetTariff": "500 TL"
}

Example 2:
Input: "Marka/ Referans Ankara'da Güney Batı Cephe Eşyalı Cam Balkonlu 2+1 Kiralık Daire Etimesgut - Devlet MahallesiDaire | 2+1 | 28. Kat | 90 m²37.500 TLTelefona Bak"
Output:
{
 "price": "37.500 TL",
 "room": "2+1",
 "sqmeter": "90 m²",
 "link": "https://www.emlakjet.com/ilan/marka-referans-ankara-da-guney-bati-cephe-esyali-cam-balkonlu-21-kiralik-daire-17354685/",
 "address": "Etimesgut - Devlet Mahallesi, Ankara",
 "waterTariff": "43.15 TL/m³",
 "naturalGasTariff": "8.34 TL/m³",
 "electricityTariff": "1456 TL/kWh",
 "internetTariff": "500 TL"
}

Example 3:
Input: "YENİ Geniş Balkonlu, Sıfır, Kiralık 1+1 Daire Beypazarı - Kurtuluş MahallesiDaire | 1+1 | 2. Kat | 50 m²13.000 TLTelefona Bak"
Output:
{
 "price": "13.000 TL",
 "room": "1+1",
 "sqmeter": "50 m²",
 "link": "https://www.emlakjet.com/ilan/genis-balkonlu-sifir-kiralik-11-daire-17356872/",
 "address": "Beypazarı - Kurtuluş Mahallesi, Ankara",
 "waterTariff": "43.15 TL/m³",
 "naturalGasTariff": "8.34 TL/m³",
 "electricityTariff": "1456 TL/kWh",
 "internetTariff": "500 TL"
}

Note: Ensure all 10+ JSON objects are correctly formatted. If there aren't enough individual listings in the input, include empty placeholder objects to reach the minimum count. For tariff information, analyze the RAG results to find and format the values into the standardized formats shown above, or set to null if not found.
"""


real_estate_agent = RealEstateAgent()
from KeywordAgent import parse_keywords
from Search import search, parse_search_links, filter_links

# Define the path for the links file
LINKS_FILE_PATH = os.path.join(os.path.dirname(__file__), 'filtered_links.txt')

def real_estate_agent_response(prompt, rag_results=None):
    try:
        # Get keywords and search for links
        keywords = parse_keywords(prompt)
        print(f"Extracted keywords: {keywords}")
        
        search_links = search(keywords)
        links = parse_search_links(search_links)
        print(f"Found {len(links)} links")
        
        filtered_links = filter_links(links)
        print(f"Filtered to {len(filtered_links)} links")
        
        if not filtered_links:
            return {"error": "No valid links found to crawl"}
            
        # Crawl the URLs
        crawled_files = crawl_urls(filtered_links)
        if not crawled_files:
            return {"error": "Failed to crawl any of the links"}
            
        # Format the crawled content for the agent
        formatted_content = "\n\n".join(crawled_files)
        
        # Add RAG results to the prompt if available
        if rag_results:
            print("\nRAG Results being added to prompt:")
            print("-" * 40)
            print(f"Number of RAG results: {len(rag_results)}")
            print("-" * 40)
            
            # Format RAG results for the prompt
            rag_content = "\n\nCost of Living Information from RAG Results:\n"
            for result in rag_results:
                rag_content += f"\nDocument: {result['document']}\n"
                rag_content += f"Source: {result['metadata']['document']}\n"
                rag_content += f"Category: {result['metadata']['category']}\n"
                rag_content += "-" * 40 + "\n"
            
            full_prompt = f"{prompt}\n\n{rag_content}\n\nCrawled content:\n{formatted_content}"
        else:
            print("\nNo RAG results available to add to prompt")
            full_prompt = f"{prompt}\n\nCrawled content:\n{formatted_content}"
        
        print("\nFull prompt being sent to agent:")
        print("-" * 40)
        print(full_prompt[:500] + "..." if len(full_prompt) > 500 else full_prompt)
        print("-" * 40)
        
        response = real_estate_agent.generate_response(full_prompt)
        return response
    except Exception as e:
        print(f"Error in real_estate_agent_response: {str(e)}")
        return {"error": f"An error occurred: {str(e)}"}

def get_rag_results(location):
    """Get RAG results for cost of living information"""
    try:
        # Initialize RAG components
        sentence_transformer_model = "distiluse-base-multilingual-cased-v1"
        collection_name = "MyDocuments"  # Changed to match the collection name in RealEstateRAG.py
        embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=sentence_transformer_model)
        chroma_client, chroma_collection = create_chroma_client(collection_name, embedding_function)
        
        # Show database information
        print("\nDatabase Information:")
        print("-" * 40)
        print(f"Collection Name: {collection_name}")
        print(f"Total Chunks: {chroma_collection.count()}")
        print("-" * 40)
        
        # Generate relevant queries
        queries = [
            f"{location} su tarifesi",
            f"{location} doğalgaz tarifesi",
            "elektrik tarifesi",  # Removed location prefix for electricity
            "internet tarifesi"   # Removed location prefix for internet
        ]
        
        print("\n" + "="*80)
        print("COST OF LIVING INFORMATION")
        print("="*80)
        
        all_results = []
        for query in queries:
            print(f"\nQuerying: {query}")
            results = retrieveDocs(chroma_collection, query, n_results=3)
            show_results(results)
            all_results.extend(results)
            
        return all_results
            
    except Exception as e:
        print(f"Error getting RAG results: {str(e)}")
        print("\nMake sure you have:")
        print("1. Installed all required packages: pip install -r requirements.txt")
        print("2. Have enough disk space for the ChromaDB database")
        print("3. Have loaded some PDF documents into the RAG system")
        return None

if __name__ == "__main__":
    # Get the location from the search query
    search_query = "Konya Kiralık Ev"
    location = search_query.split()[0]  # Get the first word as location
    
    print("\n" + "="*80)
    print("REAL ESTATE LISTINGS")
    print("="*80)
    
    # Get RAG results for cost of living FIRST
    rag_results = get_rag_results(location)
    
    # Get real estate listings (crawling and response generation)
    response = real_estate_agent_response(search_query, rag_results)
    print(response.text)