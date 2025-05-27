from google import genai
from google.genai import types

import sys
import os
sys.path.append(os.path.dirname(__file__))

from proj_market_crawl import crawl_urls
from proj_market_parser import MarketParser
import asyncio
import json

class LLM_Market_Pipeline():

    def __init__(self):

        self.website_list = [
            "https://www.akakce.com/kirmizi-et,1,2.html",
            "https://www.akakce.com/beyaz-et,1,2.html",
            "https://www.akakce.com/yumurta,1,2.html",
            "https://www.akakce.com/peynir,1,2.html",
            # "https://www.akakce.com/ekmek,1,2.html",
            # "https://www.akakce.com/pirinc,1,2.html",
            # "https://www.akakce.com/makarna,1,2.html",
            # "https://www.akakce.com/sivi-yag,1,2.html",
            # "https://www.akakce.com/seker,1,2.html",
            # "https://www.akakce.com/cay,1,2.html",
            # "https://www.akakce.com/sivi-bulasik-deterjani,1,2.html",
            # "https://www.akakce.com/toz-deterjan,1,2.html",
            # "https://www.akakce.com/tuvalet-kagidi,1,2.html",
            # "https://www.akakce.com/su.html"
        ]

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
        self.market_parser = MarketParser(
            name = "Market Parser",
            role = 
            """You are a parse helper agent that is tasked to retrieve a products name its cost and the store page link it has.

            When looking for the store page its more likely that its the link with the name of the product included. Example:
            Name = Banvit Piliç
            Link.../banvit-pilic/...html

            You are meant to put the result in a structured JSON format""",
            model = "gemini-2.5-flash-preview-04-17",
            response_type = "application/json",
            response_schema = mp_schema,
            temperature=0.1,
            timebuffer=3
        )


    def run_market_pipeline(self, prompt):
        """
        Run the entire market pipeline.
        """
        
        # Step 1: Crawl the market links
        print("Crawling market links...")
        crawl_results = asyncio.run(crawl_urls(self.website_list))
        if not crawl_results:
            print("Failed to crawl URLs.")
            return None
        
        # Step 2: Parse market listings
        print("Parsing market list...")
        # Call the agent with batches of 5
        crawl_results = [crawl_results[i:i + 5] for i in range(0, len(crawl_results), 5)]
        product_list_info = []
        for batch in crawl_results:
            # Combine all the results in the batch into a single string
            print(f"Parsing batch number: {crawl_results.index(batch) + 1}")
            batch_text = "\n".join([result for result in batch])
            batch_result = self.market_parser.generate_response(batch_text)
            if not batch_result:
                print("Failed to parse market listings.")
                return None
            
            # Append the text as a JSON to the info list
            product_list_info.append(json.loads(batch_result.text))

        #connect all the jsons into a single json by their "products" key
        product_list_info = [item for sublist in product_list_info for item in sublist['products']]

        return json.dumps(product_list_info, indent=4)

