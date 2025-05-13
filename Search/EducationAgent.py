
from google import genai

system_prompt=("""You are an financial advisor about education fees in turkey you are going to respond to user 
                according to the provided json file 
                
              """ )






client = genai.Client(api_key="AIzaSyBU3Y7wJ4RtouBAjnV7a2lcorAm4UTrZVE")
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=prompt,
    config=types.GenerateContentConfig(
        system_instruction=system_prompt,
        response_mime_type="application/json",

    )