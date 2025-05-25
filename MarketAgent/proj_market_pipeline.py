from proj_llm_agent_2 import LLM_Agent2
from google import genai
from google.genai import types
from proj_search_func import search
from proj_search_func import parse_search_results
from proj_market_parser import MarketParser
from proj_market_crawl import crawl_urls
import asyncio
import json

class LLM_Product_Pipeline():

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
        self.market_parser = LLM_Agent2(
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
            temperature=0.1,
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
        self.market_keyword_generator = LLM_Agent2(
            name = "Market Keyword Generator",
            role = 
            """You are an agent that focuses on generating turkish keywords to search for grocery market items with.

            Assume the person doesnt need tools.

            Your output must always be in JSON format.

            You must generate a list of keywords of the product in the given prompt. Youre limited to 3 keywords max.

            Dont add duplicates.

            Your results for each item should be in a json array and for each shop item you will add \"akakce\" at the start""",
            model = "gemini-2.0-flash",
            response_type = "application/json",
            response_schema = mkg_schema,
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
        self.market_searcher = LLM_Agent2(
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

        mv_schema = genai.types.Schema(
            type = genai.types.Type.OBJECT,
            required = ["should_retry", "wrong_tool"],
            properties = {
                "should_retry": genai.types.Schema(
                    type = genai.types.Type.BOOLEAN,
                ),
                "wrong_tool": genai.types.Schema(
                    type = genai.types.Type.BOOLEAN,
                ),
                "retry_reason": genai.types.Schema(
                    type = genai.types.Type.STRING,
                ),
            },
        )

        self.market_validator = LLM_Agent2(
            name = "Market Validator",
            role = 
            """
            You are a Validator Agent for Market Product Parsing. You will be given the prompt and the JSON return of the tool. Your objective is to determine if the products listed are related to the users query. Incase the tool response is insufficient the tool should be rerun. 

            The tool youre attached to fetches information about grocery products. Incase the wrong tool was used you should specify wrong_tool accordingly.

            You are to provide reasoning for your retry incase you choose to run the tool again. 
            """,
            model = "gemini-2.0-flash",
            response_type = "application/json",
            response_schema = mv_schema,
            temperature=0.95,
            timebuffer=3
        )


    def run_product_pipeline(self, prompt):
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

        links = json.loads(parsed_results.text)['links']
        #get rid of duplicates
        links = list(set(links))
        if not links:
            print("No valid links found.")
            return None

        crawl_results = asyncio.run(crawl_urls(links))

        if not crawl_results:
            print("Failed to crawl URLs.")
            return None
        

        # Step 4: Parse market listings
        print("Parsing market list...")
        product_list = self.market_parser.generate_response(json.dumps(crawl_results, indent=2))
        product_list_info = json.loads(product_list.text)

        #step 5: Validate the product list
        print("Validating product list...")
        validation_result = self.market_validator.generate_response(
            f"""user prompt: {prompt}

            tool response: {json.dumps(product_list_info, indent=4)}"""
        )

        if (json.loads(validation_result.text)['should_retry']):
            print("Validation failed, retrying...")
            retry_reason = json.loads(validation_result.text)['retry_reason']
            print(f"Retry reason: {retry_reason}")
            return self.run_product_pipeline(prompt)
        
        else:
            print("Validation successful, returning product list.")
            return json.dumps(product_list_info, indent=4)
