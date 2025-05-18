import os
import time
from google import genai
from google.genai import types
from google.genai.errors import ClientError


class LLM_Agent:
    import os
    from dotenv import load_dotenv
    load_dotenv()
    def __init__(self, name, role, response_mime_type,model = "gemini-2.0-flash", temperature=0.95,timebuffer=3):
        self.name = name
        self.role = role
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = model
        self.temperature = temperature
        self.response_mime_type = response_mime_type
        self.timebuffer = timebuffer

        self.gen_config = types.GenerateContentConfig(
            response_mime_type=self.response_mime_type,
            system_instruction=[
                types.Part.from_text(text=self.role),
            ],
        )

    def generate_response(self, contents,file_path=""):
        try:
            myfile = self.client.files.upload(file=file_path)
            response = self.client.models.generate_content(
            model=self.model,
            contents= [contents,myfile],
                config={
                    "response_mime_type": self.response_mime_type,
                    "system_instruction": self.role,
                },
            )
            return response
        
        except ClientError as e:
            error = e.details['error']['details'] # Fetching error details. Comes off as a list.

            for detail in error:

                if detail.get("@type") == "type.googleapis.com/google.rpc.RetryInfo":  # This type specifically has our retry delay.

                    retry_str = detail.get("retryDelay") #It comes off as the format (time)s
                    retry_time = int(retry_str[:-1])

                    print ("Rate limit exceeded. Waiting for",(retry_time + self.timebuffer), "seconds.")
                    time.sleep(retry_time + self.timebuffer)

                    return self.generate_response(contents)

