import os
import time
import logging
from google import genai
from google.genai import types
from google.genai.errors import ClientError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('LLM_Agent')

# Gemini pricing (as of March 2024)
GEMINI_PRO_PRICING = {
    "input": 0.00025,  # $ per 1K characters
    "output": 0.0005,  # $ per 1K characters
}

class LLM_Agent:
    import os
    from dotenv import load_dotenv
    load_dotenv()
    def __init__(self, name, role, response_mime_type, model="gemini-2.0-flash", temperature=0.95, top_p=0.9, top_k=40, timebuffer=3):
        logger.info(f"Initializing LLM_Agent with name: {name}")
        logger.info(f"Model: {model}, Temperature: {temperature}, Top_p: {top_p}, Top_k: {top_k}")
        
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

        logger.info("Creating generation config")
        self.gen_config = types.GenerateContentConfig(
            response_mime_type=self.response_mime_type,
            system_instruction=[
                types.Part.from_text(text=self.role),
            ],
        )
        logger.info("LLM_Agent initialization complete")

    def calculate_cost(self, input_chars, output_chars):
        """Calculate cost based on input and output characters"""
        input_cost = (input_chars / 1000) * GEMINI_PRO_PRICING["input"]
        output_cost = (output_chars / 1000) * GEMINI_PRO_PRICING["output"]
        return input_cost + output_cost

    def get_usage_stats(self):
        """Get current usage statistics"""
        return {
            "total_input_tokens": self.total_tokens["input"],
            "total_output_tokens": self.total_tokens["output"],
            "total_cost": self.total_cost,
            "estimated_cost_per_request": self.calculate_cost(
                self.total_tokens["input"],
                self.total_tokens["output"]
            )
        }

    def generate_response(self, contents):
        try:
            logger.info(f"Generating response for content length: {len(contents)} characters")
            logger.info(f"Using model: {self.model} with temperature={self.temperature}, top_p={self.top_p}, top_k={self.top_k}")
            
            # Count input tokens
            input_chars = len(contents)
            self.total_tokens["input"] += input_chars
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=[contents],
                config={
                    "response_mime_type": self.response_mime_type,
                    "system_instruction": self.role,
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                    "top_k": self.top_k
                },
            )
            
            # Get usage metadata from response
            if hasattr(response, 'usage_metadata'):
                output_chars = len(response.text)
                self.total_tokens["output"] += output_chars
                
                # Calculate and log cost
                request_cost = self.calculate_cost(input_chars, output_chars)
                self.total_cost += request_cost
                
                logger.info(f"Token usage - Input: {input_chars}, Output: {output_chars}")
                logger.info(f"Estimated cost for this request: ${request_cost:.6f}")
                logger.info(f"Total cost so far: ${self.total_cost:.6f}")
            
            logger.info("Response generated successfully")
            return response
        
        except ClientError as e:
            logger.error(f"ClientError occurred: {str(e)}")
            error = e.details['error']['details']

            for detail in error:
                if detail.get("@type") == "type.googleapis.com/google.rpc.RetryInfo":
                    retry_str = detail.get("retryDelay")
                    retry_time = int(retry_str[:-1])
                    wait_time = retry_time + self.timebuffer
                    
                    logger.warning(f"Rate limit exceeded. Waiting for {wait_time} seconds")
                    time.sleep(wait_time)
                    
                    logger.info("Retrying request after rate limit wait")
                    return self.generate_response(contents)

