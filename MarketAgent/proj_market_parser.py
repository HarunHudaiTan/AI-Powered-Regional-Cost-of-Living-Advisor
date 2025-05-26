from proj_llm_agent import LLM_Agent
from google import genai
from google.genai import types

from proj_llm_agent_alt import LLM_Agent_Alt


class MarketParser(LLM_Agent_Alt):

    def __init__(self, name, role, model = "gemini-2.5-flash-preview-04-17", response_type = "text/plain", response_schema = None,tools = [], temperature=0.95,timebuffer=3):
        self.name = name
        self.role = role
        self.client = genai.Client(api_key="AIzaSyAKkIfLh6xe-CjVJLI-QSgD25_8sIf_fMk",)
        self.model = model
        self.temperature = temperature
        self.timebuffer = timebuffer

        self.gen_config = types.GenerateContentConfig(
            response_mime_type = response_type,
            response_schema = response_schema,
            thinking_config = types.ThinkingConfig(
            thinking_budget=0,
            ),
            tools = tools,
            temperature = self.temperature,
            system_instruction = [
                types.Part.from_text(text=self.role),
            ],
        )

thing = MarketParser(
            name = "Market Parser",
            role = 
            """You are a parse helper agent that is tasked to retrieve a products name its cost and the store page link it has.

            When looking for the store page its more likely that its the link with the name of the product included. Example:
            Name = Banvit Piliç
            Link.../banvit-pilic/...html

            You are meant to put the result in a structured JSON format""",
            model = "gemini-2.5-flash-preview-04-17",
            response_type = "application/json",
            response_schema = None,
            temperature=0.1,
            timebuffer=3
        )
