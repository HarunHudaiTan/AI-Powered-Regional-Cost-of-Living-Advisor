import json
import os

from Agent import Agent

class RealEstateAgent(Agent):
    system_instruction = """
You are a Real Estate Advisor AI. Your purpose is to provide structured information about real estate property prices based on a user's query, using data *exclusively* from a `rentals_json` file.

You will analyze the data in the `rentals_json` file and respond with a JSON object conforming to the following schema:

```json
{
  "properties": [
    {
      "price": "Number (Price in Turkish Lira - TRY. Read from the provided rentals_json file)"
    }
  ],
  "summary": "String (A brief overview of the found properties and the search criteria used. Max 3 sentences). Includes the average price of all listed rentals. If no results found, clearly state 'No prices found matching the criteria, and no rentals_json file was available to process.'.",
  "average_price": "Number (The average price of all properties listed in the rentals_json file. Null if no prices are available).",
  "number_of_result": "Number(the count of result that matches the search criteria. If no results found, value is 0)"
}
    """

    def __init__(self):

        super().__init__(self.system_instruction, response_mime_type="application/json")

        self.real_estate_agent = Agent(self.system_instruction, response_mime_type="application/json")

    def read_json_file(self, folder_path, file_name):
        """
        Reads a JSON file from the specified folder and returns its contents.

        Parameters:
            folder_path (str): The path to the folder containing the JSON file.
            file_name (str): The name of the JSON file (with .json extension).

        Returns:
            dict or list: Parsed JSON content.
        """
        file_path = os.path.join(folder_path, file_name)

        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        return data

    def response_from_json(self, folder_path, file_name):
        """
        Reads a JSON file and uses its content as the prompt for the agent.

        Parameters:
            folder_path (str): Path to the folder containing the JSON file.
            file_name (str): Name of the JSON file.

        Returns:
            str: The response from the agent, based on the JSON content.
        """
        json_data = self.read_json_file(folder_path, file_name)

        # Convert the JSON data to a string that can be used as a prompt.  Handle different types.
        if isinstance(json_data, dict) or isinstance(json_data, list):
            prompt = json.dumps(json_data) # Convert to string to send to the model.
        else:
            prompt = str(json_data)

        return self.response(prompt)




if __name__ == '__main__':
    # Set GOOGLE_API_KEY in environment variables

    real_estate_agent = RealEstateAgent()
    folder_path = "./"  # Replace with the actual folder path
    file_name = "rentals.json"  # Replace with the actual file name


    try:
        response = real_estate_agent.response_from_json(folder_path, file_name)
        print(response)
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Make sure the GOOGLE_API_KEY is set as an environment variable.")
        print("Ensure you have a 'data' folder with a 'property.json' file (or modify the folder_path and file_name variables accordingly)")



