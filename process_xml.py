import os
from lxml import etree
import re
import csv


# Function to process each XML file
def process_xml(file_path):
    try:
        # Load the XML content (from a file)
        root = etree.parse(file_path)

        # XPath query to get TextRegion id, TextLine id, and TextEquiv text without nested Word tags
        result = root.xpath(
            '//ns:TextRegion/ns:TextLine[ns:TextEquiv[not(ancestor::ns:Word)]]',
            namespaces={'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}
        )

        if result is None:
            # Log file name if no TextEquiv tag is found
            with open(os.path.join(output_path, "image_htr_error.txt"), "a+") as error_log:
                error_log.write(f"{file_path}\n")
            print(f"No TextEquiv tag found in {file_path}. Logged in image_htr_error.txt.")

        output_file = os.path.splitext(file_path)[0] + ".csv"
        with open(output_file, "w") as f:
            csvwriter = csv.writer(f)
            # Write header row
            csvwriter.writerow(["TextRegion ID", "TextLine ID", "TextEquiv Text"])

            # Extract and print the required information
            for line in result:
                text_region_id = line.getparent().get("id")
                text_line_id = line.get("id")
                text_equiv_text = line.find("ns:TextEquiv/ns:PlainText", namespaces={
                    'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}).text
                csvwriter.writerow([text_region_id, text_line_id, text_equiv_text])

    except etree.XMLSyntaxError:
        print(f"Error parsing {file_path}. File may be malformed.")


# Walk through all .xml files in the folder
def process_all_xml_files(folder):
    for root_dir, _, files in os.walk(folder):
        for file_name in sorted(files):
            if file_name.endswith(".xml"):
                file_path = os.path.join(root_dir, file_name)
                print(f"Processing xml: {file_path}...\n")
                process_xml(file_path)


# Example usage
input_path = "image_samples/page"
output_path = 'output'
process_all_xml_files(input_path)