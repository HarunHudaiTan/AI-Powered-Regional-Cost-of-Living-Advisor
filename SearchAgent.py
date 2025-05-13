
import json
from Agent import Agent
from Keyword_Agent import parse_keyword_agent
from Search import parse_search_results
from Search import search
import os
from url_extractor import extract_and_save_urls

class SearchAgent(Agent):
    system_instructions = """
       You are a helpful search assistant. Your sole goal is
                            to understand the user's intent and provide a comprehensive
                            and concise answer based on the *provided* Google search results.
                            If the provided results are insufficient to answer the query,
                            clearly state that the information is incomplete and specify
                            what information is missing.  Do not fabricate information
                            or make assumptions. You will give a JSON structured output as answer

                            Example:

                            * User Query: "Will it be hot tomorrow?"
                            * Google Search Results:
                            Title: Ankara, Ankara, Türkiye Weather Forecast
                            Snippet: 10-Day Weather Forecast ; Today. 11/1. 65° 34°. Sunshine. Night: Clear and chilly ; Sat. 11/2. 68° 34°. Mostly cloudy. Partly cloudy and chilly ; Sun. 11/3. 60° 39 ...
                            Link: https://www.accuweather.com/en/tr/ankara/316938/weather-forecast/316938

                            Title: 10-Day Weather Forecast for Ankara, Ankara, Türkiye
                            Snippet: Some clouds this evening will give way to mainly clear skies overnight. Low around 40F. Winds light and variable. Humidity58%. UV Index0 of 11.
                            Link: https://weather.com/weather/tenday/l/Ankara+Ankara+T%C3%BCrkiye?canonicalCityId=4661d3b651b790261b56f460ed677bde63b92a88100b36f79f56e046932783e8
                            ...
                            if there is not enough information fill the more_information part.

                     {
                                 "expected_json_output": 
                                 {
                                   "user_query": "Will it be hot tomorrow?",
                                   "google_search_results":[ {
                                     "title": "Ankara, Ankara, Türkiye Weather Forecast",
                                     "snippet": "10-Day Weather Forecast ; Today. 11/1. 65° 34°. Sunshine. Night: Clear and chilly ; Sat. 11/2. 68° 34°. Mostly cloudy. Partly cloudy and chilly ; Sun. 11/3. 60° 39 ...",
                                     "sources": [
                                       "https://www.accuweather.com/en/tr/ankara/316938/weather-forecast/316938", 
                                       "https://weather.com/weather/tenday/l/Ankara+Ankara+T%C3%BCrkiye?canonicalCityId=4661d3b651b790261b56f460ed677bde63b92a88100b36f79f56e046932783e8"
                                     ]
                                   }],
                                   "answer": "Tomorrow, November 2nd, in Ankara, Turkey, the weather will be mostly cloudy with a high of 68°F and a low of 34°F. It is expected to be partly cloudy and chilly.",
                                   "missing_information":"More information can be found in the website"
                                 }
                               }
                            Provide related links in your answer if you use information from that link.  Use clear and concise language.
                            REMEMBER ALWAYS PROVIDE LINKS
       """
    def __init__(self):

        super().__init__(self.system_instructions, "application/json")

        self.search_agent = Agent(self.system_instructions, "application/json")

    def response(self,message,history):
        keyword= parse_keyword_agent(message["text"])
        results=search(keyword)
        parsed_results=parse_search_results(results)
        string_parsed_results=json.dumps(parsed_results)
        response= self.search_agent.response("User query" + message["text"] + "Google search results" + string_parsed_results)
        
        # Extract URLs from response and save to file
        try:
            extract_and_save_urls(response)
        except Exception as e:
            print(f"Error extracting URLs: {str(e)}")
        
        return response


agent=SearchAgent()
import gradio as gr
demo = gr.ChatInterface(
    fn=agent.response,
    type="messages",
    title="SearchGPT :)",
    multimodal=True
)
demo.launch()