

from google import genai
from google.genai import types
import json
class Agent:

    def __init__(self, system_prompt,response_mime_type,api_key):

        self.system_prompt = system_prompt
        self.response_mime_type = response_mime_type
        self.api_key = api_key



    def response(self,prompt):
        client=genai.Client(api_key=self.api_key)
        response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=self.system_prompt,
            response_mime_type="application/json",

        )
        )
        return response.text;