from proj_llm_agent_alt import LLM_Agent_Alt
from google import genai
from google.genai import types
from proj_search_func import search
from proj_search_func import parse_search_results
from proj_market_crawl import crawl_urls
import asyncio
import json

class LLM_Market_Pipeline():

    def __init__(self):
        mp_schema = genai.types.Schema(
            type = genai.types.Type.OBJECT,
            required = ["products"],
            properties = {
                "products": genai.types.Schema(
                    type = genai.types.Type.ARRAY,
                    items = genai.types.Schema(
                        type = genai.types.Type.OBJECT,
                        required = ["product_name", "product_cost", "product_link"],
                        properties = {
                            "product_name": genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                            "product_cost": genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                            "product_link": genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                        },
                    ),
                ),
            },
        )
        self.market_parser = LLM_Agent_Alt(
            name = "Market Parser",
            role = 
            """You are a parse helper agent that is tasked to retrieve a products name its cost and the store page link it has.

            When looking for the store page its more likely that its the link with the name of the product included. Example:
            Name = Banvit Piliç
            Link.../banvit-pilic/...html

            You are meant to put the result in a structured JSON format""",
            model = "gemini-2.0-flash",
            response_type = "application/json",
            response_schema = mp_schema,
            temperature=0.95,
            timebuffer=3
        )

        mkg_schema = genai.types.Schema(
            type = genai.types.Type.OBJECT,
            required = ["items"],
            properties = {
                "items": genai.types.Schema(
                    type = genai.types.Type.ARRAY,
                    items = genai.types.Schema(
                        type = genai.types.Type.STRING,
                    ),
                ),
            },
        )
        self.market_keyword_generator = LLM_Agent_Alt(
            name = "Market Keyword Generator",
            role = 
            """You are an agent that focuses on generating turkish keywords to search for grocery market items with.

            Assume the person doesnt need tools.

            Your output must always be in JSON format.

            Try to have less or equal to 10 keywords.

            Try to reduce variants but if needed add them.Only add them if your list isnt full. For Example:
            Red Meat = Lamb, Beef

            Your results for each item should be in a json array and for each shop item you will add \"akakce\" at the start""",
            model = "gemini-2.0-flash",
            response_type = "application/json",
            response_schema = mkg_schema,
            temperature=0.95,
            timebuffer=3
        )

        mpp_schema = genai.types.Schema(
            type = genai.types.Type.OBJECT,
            required = ["product_name", "product_cost", "product_stores"],
            properties = {
                "product_name": genai.types.Schema(
                    type = genai.types.Type.STRING,
                ),
                "product_cost": genai.types.Schema(
                    type = genai.types.Type.STRING,
                ),
                "product_stores": genai.types.Schema(
                    type = genai.types.Type.ARRAY,
                    items = genai.types.Schema(
                        type = genai.types.Type.OBJECT,
                        required = ["store_name", "store_cost"],
                        properties = {
                            "store_name": genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                            "store_cost": genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                        },
                    ),
                ),
            },
        )
        self.market_product_parser = LLM_Agent_Alt(
            name = "Market Keyword Generator",
            role = 
            """You are a parsing agent thats focused on retrieving a products name price and what stores its available on. 
            The markdown youre provided with is on a singular product and you should focus on the said product. 
            When writing down the store only write the store name. Nothing more
            You need to write your output in a JSON format.""",
            model = "gemini-2.0-flash",
            response_type = "application/json",
            response_schema = mpp_schema,
            temperature=0.95,
            timebuffer=3
        )

        ms_schema = genai.types.Schema(
            type = genai.types.Type.OBJECT,
            required = ["links"],
            properties = {
                "links": genai.types.Schema(
                    type = genai.types.Type.ARRAY,
                    items = genai.types.Schema(
                        type = genai.types.Type.STRING,
                    ),
                ),
            },
        )
        self.market_searcher = LLM_Agent_Alt(
            name = "Market Searcher",
            role = 
            """
            You are a search agent thats focused on looking for the specific website akakce.
            You will be given a dictionary of search results each being for one keyword.
            You need to look for the first link that contains the word "akakce" in it. The form youre looking for is:
            https://www.akakce.com/(product).html
            You are also tasked to modify the link URL as follows:
            https://www.akakce.com/un.html => https://www.akakce.com/un,1,6.html
            What this does is it adds ",1,6" to the url. This allows the page to list on cheapest order.
            Your outputs must be the links you make from the JSON array of keywords.
            """,
            model = "gemini-2.0-flash",
            response_type = "application/json",
            response_schema = ms_schema,
            temperature=0.95,
            timebuffer=3
        )


    def run_market_pipeline(self, prompt):
        """
        Run the entire market pipeline.
        """
        # Step 1: Generate market keywords
        print("Generating market keywords...")
        keywords = self.market_keyword_generator.generate_response(prompt)
        if not keywords:
            print("Failed to generate market keywords.")
            return None
        
        # Step 2: EducationAgent for products
        # Do a search for each keyword and send it to the market searcher
        print("Searching for products...")
        search_results = []
        for keyword in keywords.parsed['items']:
            search_result = search(keyword)
            if search_result:
                parsed_results = parse_search_results(search_result)

                search_results.append([keyword, parsed_results])
            else:
                print(f"Failed to search for keyword: {keyword}")
        
        # Step 3: Parse search results
        print("Parsing search results...")
        parsed_results = self.market_searcher.generate_response(json.dumps(search_results, indent=2))
        if not parsed_results:
            print("Failed to parse search results.")
            return None


        crawl_results = asyncio.run(crawl_urls(parsed_results.parsed['links']))

        if not crawl_results:
            print("Failed to crawl URLs.")
            return None
        
        # Step 4: Parse market listings
        print("Parsing market list...")
        product_list_info = self.market_parser.generate_response(json.dumps(crawl_results, indent=1))
    

        print(product_list_info)

        return product_list_info