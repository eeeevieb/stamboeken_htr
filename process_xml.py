import os
from lxml import etree
import re

# Define the pattern for "folio <integer>"
pattern = re.compile(r'folio\s+\d+', re.IGNORECASE)


# Function to process each XML file
def process_xml(file_path):
    try:
        # Parse the XML file
        tree = etree.parse(file_path)
        root = tree.getroot()

        # Check if the PlainText tag exists
        plain_text_found = False
        for element in root.iter("PlainText"):
            plain_text_found = True
            # Check if the text matches the pattern "folio <integer>"
            if element.text and pattern.search(element.text):
                print(f"File: {file_path} | Tag: {element.tag} | Text: {element.text}")

        # If no PlainText tag was found, log the file name
        if not plain_text_found:
            with open("image_htr_error.txt", "a") as error_log:
                error_log.write(f"{file_path}\n")
            print(f"No PlainText tag found in {file_path}. Logged in image_htr_error.txt.")

    except etree.XMLSyntaxError:
        print(f"Error parsing {file_path}. File may be malformed.")


# Walk through all .xml files in the folder
def process_all_xml_files(folder):
    for root_dir, _, files in os.walk(folder):
        for file_name in files:
            if file_name.endswith(".xml"):
                file_path = os.path.join(root_dir, file_name)
                process_xml(file_path)


# Example usage
folder_path = "image_samples/page"  # Replace with your folder path
process_all_xml_files(folder_path)