
from google import genai
from google.genai import types

from proj_llm_agent_2 import LLM_Agent2


class MarketParser(LLM_Agent2):

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
