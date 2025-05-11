import json
import os

from Agent import Agent

class RealEstateAgent(Agent):
    system_instruction = """
    
    You are a Real Estate Advisor AI. Your purpose is to provide structured information about real estate properties based on a user's query.

You will analyze the user's request and respond with a JSON object conforming to the following schema:

```json
{
  "properties": [
    {
      "address": "String (Full address of the property)",
      "price": "Number (Price in Turkish Lira - TRY)",
      "property_type": "String ('Apartment', 'House', 'Villa', 'Commercial', 'Land', etc.)",
      "bedrooms": "Number (Number of bedrooms.  Null if unknown or not applicable)",
      "bathrooms": "Number (Number of bathrooms. Null if unknown or not applicable)",
      "square_meters": "Number (Living area in square meters)",
      "description": "String (Concise description of the property highlights - max 2 sentences)",
      "amenities": "Array of Strings (List of key amenities: 'Balcony', 'Garden', 'Parking', 'Pool', 'Sea View', 'Central Heating', 'Air Conditioning', 'Security', 'Elevator', etc.  Only include amenities that are explicitly stated)",
      "location_details": "String (Description of the neighborhood/area - e.g., 'Close to public transportation', 'Quiet residential area', 'Near shopping malls')",
      "url": "String (URL link to the original property listing)",
      "contact_phone": "String(The contact number)",
    }
  ],
  "summary": "String (A brief overview of the found properties and the search criteria used. Max 3 sentences). If no results found, clearly state 'No properties found matching the criteria.'"
  "number_of_result": "Number(the count of result that matches the search criteria)"
}

Important Guidelines:

JSON Output Only: You MUST respond ONLY with valid JSON. Do NOT include any introductory text, explanations, or apologies outside the JSON structure. If you cannot fulfill the request, the "properties" array should be empty ([]), and the "summary" should state "No properties found matching the criteria.". and the "number_of_result" value should be "0"

Accuracy: Prioritize accuracy. If specific information is missing, leave the corresponding field as null or an empty array ([]) as appropriate (following the schema above). Do not guess or make up information.

Data Sources: Base your response on the data that i will provide you with string formatted google serach result.

Turkish Context: All prices should be in Turkish Lira (TRY). Location descriptions should be relevant to Turkey.

Conciseness: Be brief and to-the-point. Focus on the most relevant details for each property.

Amenity Selection: Only list amenities explicitly mentioned in the provided listing information. Do not infer amenities.

Location Details: Try to extract location details from the listing. Use words like: central, peaceful, near metro or bus station, close to public transportation and etc.

Example:
User Query: "Find apartments for sale in Kadıköy, Istanbul with at least 2 bedrooms and a balcony."

Acceptable JSON Output (example - you'll fill this based on the provided search results):

{
  "properties": [
    {
      "address": "Caferağa Mahallesi, Kadıköy, Istanbul",
      "price": 2500000,
      "property_type": "Apartment",
      "bedrooms": 2,
      "bathrooms": 1,
      "square_meters": 85,
      "description": "Modern 2-bedroom apartment in a central Kadıköy location. Features a balcony and updated kitchen.",
      "amenities": ["Balcony", "Central Heating", "Elevator"],
      "location_details": "Centrally located near cafes and shops, close to public transportation.",
      "url": "https://example.com/listing123",
      "contact_phone": "0532 123 4567"
    },
    {
      "address": "Osmanağa Mahallesi, Kadıköy, Istanbul",
      "price": 3000000,
      "property_type": "Apartment",
      "bedrooms": 3,
      "bathrooms": 2,
      "square_meters": 110,
      "description": "Spacious 3-bedroom apartment with a sea view in a desirable Kadıköy neighborhood. Includes a large balcony.",
      "amenities": ["Balcony", "Sea View", "Parking", "Security"],
      "location_details": "Peaceful residential area with easy access to the ferry terminal.",
      "url": "https://example.com/listing456",
      "contact_phone": "0532 987 6543"
    }
  ],
  "summary": "Found 2 apartments for sale in Kadıköy, Istanbul with at least 2 bedrooms and a balcony.",
  "number_of_result": "2"
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
    folder_path = "./Parsed_Docs"  # Replace with the actual folder path
    file_name = "temp_crawl_result.json"  # Replace with the actual file name

    # Create a dummy property.json file if one doesn't exist:
    if not os.path.exists(os.path.join(folder_path, file_name)):
        os.makedirs(folder_path, exist_ok=True)
        with open(os.path.join(folder_path, file_name), "w") as f:
            json.dump({"address": "123 Main St", "bedrooms": 3, "bathrooms": 2, "price": 500000}, f)


    try:
        response = real_estate_agent.response_from_json(folder_path, file_name)
        print(response)
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Make sure the GOOGLE_API_KEY is set as an environment variable.")
        print("Ensure you have a 'data' folder with a 'property.json' file (or modify the folder_path and file_name variables accordingly)")



