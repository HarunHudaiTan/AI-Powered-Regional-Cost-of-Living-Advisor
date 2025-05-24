import json
import os
import time
import logging
from google import genai
from google.genai import types
from google.genai.errors import ClientError
import logging as logger
from dotenv import load_dotenv
load_dotenv()
class CreateChat:
    def __init__(self, name, role, response_mime_type, model="gemini-2.0-flash", temperature=0.95, top_p=0.9, top_k=40,
                 timebuffer=3):
        # logger.info(f"Initializing LLM_Agent with name: {name}")
        # logger.info(f"Model: {model}, Temperature: {temperature}, Top_p: {top_p}, Top_k: {top_k}")

        self.name = name
        self.role = role
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.response_mime_type = response_mime_type
        self.timebuffer = timebuffer
        self.total_tokens = {"input": 0, "output": 0}
        self.total_cost = 0.0
        self.chat=self.client.chats.create(model=self.model,
                config={
                    "response_mime_type": self.response_mime_type,
                    "system_instruction": self.role,
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                    "top_k": self.top_k
                })


    def send_message(self, message):
            logger.info(f"Sending message: {message}")
            response = self.chat.send_message(message)
            response_json=json.loads(response.text)
            return response_json

