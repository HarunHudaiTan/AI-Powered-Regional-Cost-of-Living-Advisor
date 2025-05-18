from google.genai import types

class Function_Agent(Agent):
    system_instructions = (
        "You are an agent that provides users with fuel price data. "
    )

    # Define a function that the model can call to fetch fuel prices for a Turkish city
    fetch_fuel_prices_declaration = {
        "name": "fetch_fuel_prices",
        "description": "Fetches fuel prices for a certain Turkish city as markdown.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": """Name of the Turkish city.
                                      Must be in lowercase using only English alphabet characters.
                                      For example, 'ankara', 'istanbul', 'izmir', "karabuk", "agri".
                                      Convert uppercase (e.g., 'A', 'B', 'Y') to lowercase ('a', 'b', 'y')
                                      Convert Turkish characters (e.g., 'ğ', 'ş', 'ç', 'ü', 'ı', 'ö') to their English equivalents ('g', 's', 'c', 'u', 'i', 'o').""",
                },
            },
            "required": ["city"],
        },
    }


    transport_tools = [types.Tool(function_declarations=[fetch_fuel_prices_declaration])]

    tool_config = types.ToolConfig(
        function_calling_config=types.FunctionCallingConfig(
            mode="ANY"  # Use "ANY" to force function call suggestions
        )
    )

    config = types.GenerateContentConfig(
                system_instruction=system_instructions,
                tools=transport_tools,
                tool_config=tool_config
            )

    def __init__(self):
        super().__init__(self.config)


agent = Function_Agent()
response = agent.response("İstanbul akaryakıt fiyatları")

print(response.function_calls)


# Check for function call suggestion
function_call = response.candidates[0].content.parts[0].function_call if response.candidates[0].content.parts else None

if function_call:
    print(f"Function to call: {function_call.name}")
    print(f"Arguments: {function_call.args}")
else:
    print("No function call suggested by the model.")
  