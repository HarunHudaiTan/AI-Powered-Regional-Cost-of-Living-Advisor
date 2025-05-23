from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

class Agent:
    def __init__(self, system_config):
        load_dotenv()  # Load environment variables from .env file
        self.system_config = system_config

    def response(self, prompt):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[types.Content(role="user", parts=[types.Part(text=prompt)])],
            config=self.system_config
        )
        return response