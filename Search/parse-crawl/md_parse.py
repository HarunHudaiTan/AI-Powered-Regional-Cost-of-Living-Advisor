import re
import json


def extract_markdown_sections_from_file(file_path):
    """
    Extract sections from a text file containing markdown-formatted content
    based on ## and ### headings and return them as a structured JSON object.

    Args:
        file_path (str): Path to the text file with markdown content

    Returns:
        dict: JSON-serializable dictionary with sections and their content
    """
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as file:
            markdown_text = file.read()

        return extract_markdown_sections_from_text(markdown_text)

    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return {"error": str(e)}


def extract_markdown_sections_from_text(markdown_text):
    """
    Extract sections from a markdown-formatted text string
    based on ## and ### headings and return them as a structured JSON object.

    Args:
        markdown_text (str): Markdown-formatted content as a string

    Returns:
        dict: JSON-serializable dictionary with sections and their content
    """
    try:
        # Dictionary to store the structured data
        result = {}

        # Split the markdown into lines
        lines = markdown_text.split('\n')

        current_h2 = None
        current_h3 = None
        current_content = []

        # Process each line
        for line in lines:
            # Check if the line starts with ## (level 2 heading)
            if line.startswith('## '):
                # If we were collecting content for a previous section, save it
                if current_h3 is not None:
                    # Add the content to the current h3 section
                    if current_h2 not in result:
                        result[current_h2] = {}
                    result[current_h2][current_h3] = current_content
                    current_content = []

                # Set the new h2 heading
                current_h2 = line[3:].strip()
                current_h3 = None

            # Check if the line starts with ### (level 3 heading)
            elif line.startswith('### '):
                # If we were collecting content for a previous section, save it
                if current_h3 is not None:
                    # Add the content to the current h3 section
                    if current_h2 not in result:
                        result[current_h2] = {}
                    result[current_h2][current_h3] = current_content
                    current_content = []

                # Set the new h3 heading
                current_h3 = line[4:].strip()
                current_content = []

            # If line is not a heading and we have an active h3 section, collect content
            elif current_h3 is not None:
                # Only add non-empty lines
                if line.strip():
                    current_content.append(line.strip())

        # Don't forget to add the last section if there is any
        if current_h3 is not None and current_h2 is not None:
            if current_h2 not in result:
                result[current_h2] = {}
            result[current_h2][current_h3] = current_content

        return result

    except Exception as e:
        print(f"Error processing markdown text: {str(e)}")
        return {"error": str(e)}


def save_to_json_file(sections, output_file_path):
    """
    Save the extracted sections to a JSON file.

    Args:
        sections (dict): The extracted sections
        output_file_path (str): Path to save the JSON file

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(output_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(sections, json_file, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving JSON file: {str(e)}")
        return False


# Main function to use
def markdown_to_json(input_file_path, output_file_path=None):
    """
    Process a markdown file and extract sections into JSON.

    Args:
        input_file_path (str): Path to the input text file with markdown content
        output_file_path (str, optional): Path to save the JSON output.
                                         If None, returns the JSON as a string.

    Returns:
        str or bool: JSON string if output_file_path is None, else success status
    """
    sections = extract_markdown_sections_from_file(input_file_path)

    if output_file_path:
        return save_to_json_file(sections, output_file_path)
    else:
        # Return as formatted JSON string
        return json.dumps(sections, ensure_ascii=False, indent=2)


# New function to process markdown text directly
def markdown_text_to_json(markdown_text, output_file_path=None):
    """
    Process markdown text directly and extract sections into JSON.

    Args:
        markdown_text (str): Markdown-formatted content as a string
        output_file_path (str, optional): Path to save the JSON output.
                                         If None, returns the JSON as a string.

    Returns:
        str or bool: JSON string if output_file_path is None, else success status
    """
    sections = extract_markdown_sections_from_text(markdown_text)

    if output_file_path:
        return save_to_json_file(sections, output_file_path)
    else:
        # Return as formatted JSON string
        return json.dumps(sections, ensure_ascii=False, indent=2)

# Example usage:
# 1. To process a file and get JSON as string:
# json_data = markdown_to_json("university_links.txt")
# print(json_data)

# 2. To process a file and save JSON to another file:
# success = markdown_to_json("result.txt", "result.json")
# if success:
#     print("JSON file created successfully!")