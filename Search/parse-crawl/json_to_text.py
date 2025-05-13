import json

def format_university_data(json_file_path):
    """
    Converts university data from a JSON file into a condensed string format
    suitable for LLMs.

    Args:
        json_file_path (str): Path to the JSON file.

    Returns:
        str: A formatted string containing the university data.
    """

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        return "Error: File not found."
    except json.JSONDecodeError:
        return "Error: Invalid JSON format."

    output_string = ""

    for university, details in data.items():
        output_string += f"**{university.replace('-', ' ').title()}**:\n" # University Name

        if not details or details == {}: #Handle Empty entries
            output_string += "  No data available.\n"
            continue

        for category, program_list in details.get("null",details).items(): #Access the "null" key. If not available, it processes like a normal object
            if not program_list: continue

            output_string += f"  *{category}*:\n"
            for item in program_list:
                output_string += f"    - {item}\n" #Each item under the category.
        output_string += "\n"

    return output_string

# Example usage:
json_file = "updated_results.json"
formatted_data = format_university_data(json_file)

print(formatted_data)

with open("formatted_university_data.txt", "w", encoding="utf-8") as outfile:
    outfile.write(formatted_data)