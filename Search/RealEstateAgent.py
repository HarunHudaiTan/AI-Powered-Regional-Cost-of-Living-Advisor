from Agent import Agent
from proj_llm_agent import LLM_Agent


class RealEstateAgent(LLM_Agent):
    def __init__(self):
        super().__init__("Real Estate Agent",self.system_instructions, "application/json")


    system_instructions = """
      
    you are an real estae agent understand the given real estate information and 
    give a structured output that look like:
    dont forget to print harun every single time
    {
    "harun":"ASDFJLADNLNFDLFN"
    "price":
    "location":
    "link":
    }
    
    """

real_estate_agent=RealEstateAgent()
from KeywordAgent import parse_keywords
from Search import search,parse_search_links,filter_links

def real_estate_agent_response(prompt):
    keywords = parse_keywords(prompt)
    links = parse_search_links(keywords)
    filtered_links=filter_links(links)


    response=real_estate_agent.generate_response(prompt,"/Users/harun/Documents/GitHub/AI-Powered-Regional-Cost-of-Living-Advisor/Search/parse-crawl/crawl_results/https___www_hepsiemlak_com_ankara_kiralik_daire.txt")
    return response

response=real_estate_agent_response("what are the average rental prices of ankara ")
print(response.text)