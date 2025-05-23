from google import genai
from google.genai import types
from google.colab import userdata
class Agent:

    def __init__(self, system_config):
        self.system_config = system_config

    def response(self,prompt):
        api_key = userdata.get("GOOGLE_API_KEY")
        client=genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents = [types.Content(role="user", parts=[types.Part(text=prompt)])],
            config=self.system_config
        )

        return response;