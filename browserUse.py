from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent
from dotenv import load_dotenv
import asyncio
import json
# Read GEMINI_API_KEY into env
load_dotenv()

# Initialize the model
llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash')

# Create agent with the model
async def main():
    agent = Agent(
        task="Retrieve the domates fiyatları from https://marketfiyati.org.tr",
        llm=llm
    )
    history = await agent.run()

    result=history.final_result()
    with open('result.md', 'w', encoding='utf-8') as f:
        f.write(result)

asyncio.run(main())

