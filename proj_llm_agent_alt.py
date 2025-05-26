import os
import time
from google import genai
from google.genai import types
from google.genai.errors import ClientError

class LLM_Agent_Alt:
    def __init__(self, name, role, model="gemini-2.0-flash", response_type="text/plain", response_schema=None, tools=[],
                 temperature=0.95, timebuffer=3):
        self.name = name
        self.role = role
        self.client = genai.Client(api_key="AIzaSyAKkIfLh6xe-CjVJLI-QSgD25_8sIf_fMk", )
        self.model = model
        self.temperature = temperature
        self.timebuffer = timebuffer

        self.gen_config = types.GenerateContentConfig(
            response_mime_type=response_type,
            response_schema=response_schema,
            tools=tools,
            temperature=self.temperature,
            system_instruction=[
                types.Part.from_text(text=self.role),
            ],
        )

    def generate_response(self, contents):
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=self.gen_config,
            )
            return response

        except ClientError as e:
            # check if error is 429
            if e.code == 429:
                error = e.details['error']['details']  # Fetching error details. Comes off as a list.

                for detail in error:

                    if detail.get(
                            "@type") == "type.googleapis.com/google.rpc.RetryInfo":  # This type specifically has our retry delay.

                        retry_str = detail.get("retryDelay")  # It comes off as the format (time)s
                        retry_time = int(retry_str[:-1])

                        print("Rate limit exceeded. Waiting for", (retry_time + self.timebuffer), "seconds.")
                        time.sleep(retry_time + self.timebuffer)

                        return self.generate_response(contents)
            else:
                print("An error occurred:", e)
                return None

