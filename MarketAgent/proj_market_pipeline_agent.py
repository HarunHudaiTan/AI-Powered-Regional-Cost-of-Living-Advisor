from proj_llm_agent import LLM_Agent
from google import genai
from google.genai import types
from proj_search_func import search
from proj_search_func import parse_search_results
from proj_market_crawl import crawl_urls
import asyncio
import json

class LLM_Market_Pipeline():

    def __init__(self):

        self.website_list = [
            "https://www.akakce.com/kirmizi-et,1,2.html",
            "https://www.akakce.com/beyaz-et,1,2.html",
            "https://www.akakce.com/sucuk,1,2.html",
            "https://www.akakce.com/salam,1,2.html",
            "https://www.akakce.com/sosis,1,2.html",
            "https://www.akakce.com/ton-baligi,1,2.html",
            "https://www.akakce.com/yumurta,1,2.html",
            "https://www.akakce.com/peynir,1,2.html",
            "https://www.akakce.com/bulyon,1,2.html",
            "https://www.akakce.com/kemik-suyu,1,2.html",
            "https://www.akakce.com/salca,1,2.html",
            "https://www.akakce.com/ekmek,1,2.html",
            "https://www.akakce.com/seker,1,2.html",
            "https://www.akakce.com/un,1,2.html",
            "https://www.akakce.com/kabartma-tozu,1,2.html",
            "https://www.akakce.com/tereyagi,1,2.html",
            "https://www.akakce.com/cikolata,1,2.html",
            "https://www.akakce.com/bulgur,1,2.html",
            "https://www.akakce.com/pirinc,1,2.html",
            "https://www.akakce.com/makarna,1,2.html",
            "https://www.akakce.com/sivi-yag,1,2.html",
            "https://www.akakce.com/su,1,2.html",
            "https://www.akakce.com/gazli-icecek,1,2.html",
            "https://www.akakce.com/filtre-kahve,1,2.html",
            "https://www.akakce.com/sivi-bulasik-deterjani,1,2.html",
            "https://www.akakce.com/bulasik-makinesi-tableti,1,2.html",
            "https://www.akakce.com/camasir-suyu,1,2.html",
            "https://www.akakce.com/toz-deterjan,1,2.html"
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
        self.market_parser = LLM_Agent(
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
        self.market_natural_response = LLM_Agent(
            name = "Market Natural Language Generator",
            role = 
            """You are an agent that is tasked with deducting if the given salary is feasable to sustain the person (or family if given in prompt).
            You are focusing on the groceries that person will need to buy.
            Youre also given a list of nessesary groceries that are commonly purchased. Theyre the cheapest ones in the market.
            The list contains profucts from these categories:
            - Red Meat
            - White Meat
            - Sucuk
            - Salami
            - Sausage
            - Tuna
            - Egg
            - Cheese
            - Bouillon
            - Bone Broth
            - Tomato Paste
            - Bread
            - Sugar
            - Flour
            - Baking Powder
            - Butter
            - Chocolate
            - Bulgur
            - Rice
            - Pasta
            - Liquid Oil
            - Water
            - Soft Drink
            - Filter Coffee
            - Liquid Dishwashing Detergent
            - Dishwasher Tablet
            - Bleach
            - Powder Detergent
            You should give avarage prices when explaining and what the user can buy with the given salary.
            You should also do product suggestions with their prices.
            Dont include any products that arent given in the data given to you.
            """,
            model = "gemini-2.0-flash",
            response_type = "text/plain",
            response_schema = None,
            temperature=0.95,
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
            batch_text = "\n".join([result for result in batch])
            batch_result = self.market_parser.generate_response(batch_text)
            if not batch_result:
                print("Failed to parse market listings.")
                return None
            product_list_info.append(batch_result.text)
        
        # Step 3: Generate natural language response
        print("Generating natural language response...")
        natural_response = self.market_natural_response.generate_response([prompt, product_list_info])

        if not natural_response:
            print("Failed to generate natural language response.")
            return None
        
        return natural_response


