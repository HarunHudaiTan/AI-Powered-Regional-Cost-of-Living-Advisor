from proj_llm_agent import LLM_Agent

agent = LLM_Agent("Test Agent", "You are a chat agent.","gemini-2.0-flash")

for i in range(26):
    response = agent.generate_response("Hello, how are you?")
    print(f"Response {i+1}: {response.text}")