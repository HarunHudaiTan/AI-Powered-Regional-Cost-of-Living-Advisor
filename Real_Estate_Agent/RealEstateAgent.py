import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from proj_llm_agent import LLM_Agent
import logging
# Import the crawling functions from Crawl.py
from Crawl import crawl_urls
from Real_Estate_Agent.RealEstateRAG import retrieveDocs, show_results, create_chroma_client
from chromadb.utils import embedding_functions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('Real_Estate_Agent')

class RealEstateAgent(LLM_Agent):
    def __init__(self):
        logger.info("Initializing Real_Estate_Agent")
        # Configure LLM parameters specifically for Real_Estate_Agent
        temperature = 0.1  # Controls randomness (0.0 to 1.0)
        top_p = 0.1       # Controls diversity via nucleus sampling
        top_k = 5         # Controls diversity via top-k sampling
        logger.info(f"Setting LLM parameters - temperature: {temperature}, top_p: {top_p}, top_k: {top_k}")
        super().__init__("Real Estate Agent", self.system_instructions, "application/json", 
                        temperature=temperature, top_p=top_p, top_k=top_k)
        logger.info("Real_Estate_Agent initialization complete")

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
  * Analyze the Real_Estate_RAG results to find relevant tariff information
  * Extract and format the values into standardized formats:
    - waterTariff: Convert to "XX.XX TL/m³" format
    - naturalGasTariff: Convert to "XX.XX TL/m³" format
    - electricityTariff: 
      * If monthly price: Convert to "XXXX TL" format
      * If per kWh price: Convert to "X.XXX TL/kWh" format
    - internetTariff: Convert to "XXX TL" format
  * If a specific tariff is not found in Real_Estate_RAG results, set its value to null
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
 "electricityTariff": "XXXX TL" or "X.XXX TL/kWh" or null,
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
 "electricityTariff": "1456 TL",
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
 "electricityTariff": "1.456 TL/kWh",
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
 "electricityTariff": "1456 TL",
 "internetTariff": "500 TL"
}

Note: Ensure all 10+ JSON objects are correctly formatted. If there aren't enough individual listings in the input, include empty placeholder objects to reach the minimum count. For tariff information, analyze the Real_Estate_RAG results to find and format the values into the standardized formats shown above, or set to null if not found.
"""


real_estate_agent = RealEstateAgent()
from KeywordAgent import parse_keywords
from Search import search, parse_search_links, filter_links

# Define the path for the links file
LINKS_FILE_PATH = os.path.join(os.path.dirname(__file__), 'filtered_links.txt')

def real_estate_agent_response(prompt, rag_results=None):
    try:
        logger.info(f"Processing real estate agent response for prompt: {prompt[:100]}...")
        
        # Get keywords and search for links
        logger.info("Extracting keywords from prompt")
        keywords = parse_keywords(prompt)
        logger.info(f"Extracted keywords: {keywords}")
        
        logger.info("Searching for links")
        search_links = search(keywords)
        links = parse_search_links(search_links)
        logger.info(f"Found {len(links)} links")
        
        logger.info("Filtering links")
        filtered_links = filter_links(links)
        logger.info(f"Filtered to {len(filtered_links)} links")
        
        if not filtered_links:
            logger.warning("No valid links found to crawl")
            return {"error": "No valid links found to crawl"}
            
        # Crawl the URLs
        logger.info("Starting URL crawling")
        crawled_files = crawl_urls(filtered_links)
        if not crawled_files:
            logger.warning("Failed to crawl any of the links")
            return {"error": "Failed to crawl any of the links"}
        logger.info(f"Successfully crawled {len(crawled_files)} files")
            
        # Format the crawled content for the agent
        formatted_content = "\n\n".join(crawled_files)
        
        # Add Real_Estate_RAG results to the prompt if available
        if rag_results:
            logger.info(f"Adding {len(rag_results)} Real_Estate_RAG results to prompt")
            # Format Real_Estate_RAG results for the prompt
            rag_content = "\n\nCost of Living Information from Real_Estate_RAG Results:\n"
            for result in rag_results:
                rag_content += f"\nDocument: {result['document']}\n"
                rag_content += f"Source: {result['metadata']['document']}\n"
                rag_content += f"Category: {result['metadata']['category']}\n"
                rag_content += "-" * 40 + "\n"
            
            full_prompt = f"{prompt}\n\n{rag_content}\n\nCrawled content:\n{formatted_content}"
        else:
            logger.info("No Real_Estate_RAG results available")
            full_prompt = f"{prompt}\n\nCrawled content:\n{formatted_content}"
        
        logger.info(f"Generated full prompt of length: {len(full_prompt)} characters")
        logger.info("Generating response from agent")
        response = real_estate_agent.generate_response(full_prompt)
        logger.info("Response generated successfully")
        return response
    except Exception as e:
        logger.error(f"Error in real_estate_agent_response: {str(e)}")
        return {"error": f"An error occurred: {str(e)}"}

def get_rag_results(location):
    """Get Real_Estate_RAG results for cost of living information"""
    try:
        logger.info(f"Getting Real_Estate_RAG results for location: {location}")
        
        # Initialize Real_Estate_RAG components
        sentence_transformer_model = "distiluse-base-multilingual-cased-v1"
        collection_name = "MyDocuments"
        logger.info(f"Initializing Real_Estate_RAG with model: {sentence_transformer_model}")
        
        embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=sentence_transformer_model)
        chroma_client, chroma_collection = create_chroma_client(collection_name, embedding_function)
        
        # Show database information
        logger.info(f"Database Information - Collection: {collection_name}, Total Chunks: {chroma_collection.count()}")
        
        # Generate relevant queries
        queries = [
            f"{location} su tarifesi",
            f"{location} doğalgaz tarifesi",
            "elektrik tarifesi",
            "internet tarifesi"
        ]
        
        logger.info(f"Generated queries: {queries}")
        
        all_results = []
        for query in queries:
            logger.info(f"Querying: {query}")
            results = retrieveDocs(chroma_collection, query, n_results=3)
            show_results(results)
            all_results.extend(results)
            logger.info(f"Found {len(results)} results for query: {query}")
            
        logger.info(f"Total Real_Estate_RAG results found: {len(all_results)}")
        return all_results
            
    except Exception as e:
        logger.error(f"Error getting Real_Estate_RAG results: {str(e)}")
        logger.info("Make sure you have:")
        logger.info("1. Installed all required packages: pip install -r requirements.txt")
        logger.info("2. Have enough disk space for the ChromaDB database")
        logger.info("3. Have loaded some PDF documents into the Real_Estate_RAG system")
        return None

if __name__ == "__main__":
    # Get the location from the search query
    search_query = "istanbul kiralık ev"
    location = search_query.split()[0]  # Get the first word as location
    
    logger.info(f"Starting real estate search for query: {search_query}")
    logger.info(f"Location extracted: {location}")
    
    # Get Real_Estate_RAG results for cost of living FIRST
    logger.info("Getting Real_Estate_RAG results for cost of living information")
    rag_results = get_rag_results(location)
    
    # Get real estate listings (crawling and response generation)
    logger.info("Getting real estate listings")
    response = real_estate_agent_response(search_query, rag_results)
    
    # Get and display token usage statistics
    usage_stats = real_estate_agent.get_usage_stats()
    logger.info("\nToken Usage Statistics:")
    logger.info("=" * 50)
    logger.info(f"Total Input Tokens: {usage_stats['total_input_tokens']}")
    logger.info(f"Total Output Tokens: {usage_stats['total_output_tokens']}")
    logger.info(f"Total Cost: ${usage_stats['total_cost']:.6f}")
    logger.info(f"Cost per Request: ${usage_stats['estimated_cost_per_request']:.6f}")
    logger.info("=" * 50)
    
    logger.info("Response received, printing results")
    print(response.text)