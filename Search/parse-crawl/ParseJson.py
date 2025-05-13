import json

def remove_data(input_file, output_file):
    """
    Removes data related to the '2023-2024', '2022-2023' seasons and "Hazırlık" from a JSON file.

    Args:
        input_file (str): The path to the input JSON file.
        output_file (str): The path to the output JSON file.
    """

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{input_file}'.")
        return

    def process_data(obj):
        if isinstance(obj, dict):
            keys_to_delete = []
            for key, value in obj.items():
                if any(x in str(key) for x in ["2023", "2024", "2022"]) and ("2023-2024" in str(key) or "2022-2023" in str(key)) or "Hazırlık" in str(key):
                    keys_to_delete.append(key)
                else:
                    obj[key] = process_data(value)  # Recursive call

            for key in keys_to_delete:
                del obj[key]

        elif isinstance(obj, list):
            new_list = []
            for item in obj:
                processed_item = process_data(item)
                if not (isinstance(processed_item, str) and (any(x in processed_item for x in ["2023", "2024", "2022"]) and ("2023-2024" in processed_item or "2022-2023" in processed_item) or "Hazırlık" in processed_item)):
                    new_list.append(processed_item)  # Keep it if it does not contain the string

            obj[:] = new_list  # Replace the whole list

        return obj

    modified_data = process_data(data)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(modified_data, f, indent=2, ensure_ascii=False)

    print(f"Successfully processed '{input_file}' and saved the modified data to '{output_file}'.")


# Example usage:
input_file = 'parsed_results.json'  # Replace with your input file name
output_file = 'updated_results.json'  # Replace with your desired output file name
remove_data(input_file, output_file)