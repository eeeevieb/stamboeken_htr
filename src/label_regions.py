from typing import Any
import os
from lxml import etree
import re
import csv
import openpyxl
import argparse

def get_arguments():
    parser = argparse.ArgumentParser(description="Visualization of regions")

    parser.add_argument("-i", "--input", help="Path to input folder", type=str, default=None)
    parser.add_argument("-o", "--output", help="Path to output folder", type=str)

    args = parser.parse_args()

    return args


# """
# Pseudo-code:
#         |---------------------------|---------------------------|---------------------------------------------|--------------------------------------|---------------------------------|
#         | Case                      | Search Keyword or Pattern  | Description                                 | Regex Pattern                        | Captured Information            |
#         |---------------------------|---------------------------|---------------------------------------------|--------------------------------------|---------------------------------|
#         | **1: Vader (Father)**     | `Vader`                   | Checks if line contains "Vader"             | `.*Vader\s+(.+)`                    | Text after "Vader" (Father's name) |
#         | **2: Moeder (Mother)**    | `Moeder`                  | Checks if line contains "Moeder"            | `.*Moeder\s+(.+)`                   | Text after "Moeder" (Mother's name) |
#         | **3: Geboorte datum (DOB)**| `Geboren`                | Checks if line contains "Geboren"           | `Geboren\s+(.+)`                    | Text after "Geboren" (Date of Birth) |
#         | **4: Geboorte Plaats (Place of Birth)** | `te`        | Checks if line starts with "te"             | `^te\s+(.+)`                        | Text after "te" (Place of Birth) |
#         | **5: Laatste Woonplaats (Last Residence)** | `laatst gewoond te` | Checks if line contains "laatst gewoond te" | `laatst\s*gewoond te\s+(.+)` | Text after "laatst gewoond te" (Last Residence) |
#         | **6: Campaigns**          | `4-digit year followed by place name`| Checks if starts with 4 digit and followed by strings | `\b(\d{4})\s+([a-zA-Z]+[\sa-zA-Z]*)` | 4 digit as Year, string as place |
#         | **7: Military Postings**          | `more than 1 date pattern`| Checks if strings has more than one date patterns | `.*?[0-9]{1,2}\s[A-Z]+[a-z]*\s[1-9]{4}\.*` | String before the date as Context, date as Event Date |
# """


def label_xml(xml_file, output_file):
    """
        Labels TextLines in an XML file with the foloowing lables:
            - Name
            - Date
            - Place
            - Orde

        Parameters:
        xml_file (file): XML data as a file
        output_file: Name for output file

        Returns:
        XML file: Labeled XML

    """

    try:
        tree = etree.parse(xml_file)
        root = tree.getroot()

        new_tree = etree.ElementTree(root)

        result = new_tree.xpath(
            '//ns:TextRegion/ns:TextLine[ns:TextEquiv[not(ancestor::ns:Word)]]',
            namespaces={'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}
        )

        if result is None:
            # Log file name if no TextEquiv tag is found
            with open(os.path.join(output_path, "image_htr_error.txt"), "a+") as error_log:
                error_log.write(f"{file_path}\n")
            print(f"No TextEquiv tag found in {file_path}. Logged in image_htr_error.txt.")
            return
            
        width = result[0].getparent().getparent().get("imageWidth")
        height = result[0].getparent().getparent().get("imageHeight")

        # Extract and print the required information
        for line in result:
            text_region_id = line.getparent().get("id")
            text_equiv_text = line.find("ns:TextEquiv/ns:PlainText", namespaces={
                'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}).text
            text_coordinates = line.find("ns:Coords", namespaces={
                'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}).get("points")
            region = line

            if text_equiv_text is None:
                continue

            # Case 1: Vader --> Name
            vader_match = re.search(r'.*Vader\s+(.+)', text_equiv_text, re.IGNORECASE)
            if vader_match:
                new_region = line.get("custom")
                new_region += " structure {type:Name;}"
                line.set("custom", new_region)

            # Case 2: Moeder --> Name
            moeder_match = re.search(r'.*Moeder\s+(.+)', text_equiv_text, re.IGNORECASE)
            if moeder_match:
                new_region = line.get("custom")
                new_region += " structure {type:Name;}"
                line.set("custom", new_region)

            # Case 3: Geboortedatum (e.g., "Geboren: 01-01-1900") --> Date
            geboorte_datum_match = re.search(r'Geboren\s+(.+)^(?!.*te\s+).+$', text_equiv_text, re.IGNORECASE)
            if geboorte_datum_match:
                new_region = line.get("custom")
                new_region += " structure {type:Date;}"
                line.set("custom", new_region)

            # Case 4: Geboorteplaats (e.g., "te Amsterdam") --> Place
            geboorte_plaats_match = re.search(r'\bte\s+[A-Z]+(.+)$', text_equiv_text)
            if geboorte_plaats_match:
                new_region = line.get("custom")
                new_region += " structure {type:Place;}"
                line.set("custom", new_region)

            # Case 5: Laatste Woonplaats (e.g., "laatst gewoond te Rotterdam") --> Place
            laatste_woonplaats_match = re.search(r'laatst\s*gewoond te\s+(.+)', text_equiv_text, re.IGNORECASE)
            if laatste_woonplaats_match:
                nnew_region = line.get("custom")
                new_region += " structure {type:Place;}"
                line.set("custom", new_region)

            # Case 6: All dates --> Date
            date_match = re.search(r'[0-9]{1,2}\s[A-Z]+[a-z]*\s[1-9]{4}\.*', text_equiv_text, re.IGNORECASE)
            if date_match:
                new_region = line.get("custom")
                new_region += " structure {type:Date;}"
                line.set("custom", new_region)

            # Case 7: Years --> Date
            year_match = re.search(r'\b[1-9]{4}\b', text_equiv_text, re.IGNORECASE)
            if year_match:
                new_region = line.get("custom")
                if not re.search(r'{type:Date;}', new_region):
                    new_region += " structure {type:Date;}"
                    line.set("custom", new_region)

            # Case 8: Orde (e.g. 'Ridder van de Willems Orde') --> Orde
            orde_match = re.search(r'\borde\b', text_equiv_text, re.IGNORECASE)
            if orde_match:
                new_region = line.get("custom")
                new_region += " structure {type:Orde;}"
                line.set("custom", new_region)

            # Case 9: All names --> Name
            name_match = re.search(r'^[A-Z][a-z]*(?:[\s\W]+[A-Z][a-z]*)+[.!?]?$', text_equiv_text)
            if name_match:
                if float(text_coordinates.split(",")[0]) < (int(width) / 4):
                    new_region = line.get("custom")
                    if not re.search(r'{type:Name;}', new_region):
                        new_region += " structure {type:Name;}"
                    line.set("custom", new_region)

        # Save filee
        new_file = xml_file.split('/')[-1].strip('_fixed.xml')
        output_dir = f"{output_file}/labeled"
        os.makedirs(output_dir, exist_ok=True)
        new_tree.write(f'{output_file}/labeled/{new_file}_labeled.xml', pretty_print=True, xml_declaration=True, encoding="UTF-8")
        print(f'File saved at {output_file}/labeled/{new_file}_labeled.xml')

    except etree.XMLSyntaxError:
        print(f"Error parsing {xml_file}. File may be malformed.")


# Walk through all .xml files in the folder
def process_all_xml_files(folder_input, folder_output):
    for root_dir, _, files in os.walk(folder_input):
        for file_name in sorted(files):
            if file_name.endswith(".xml"):
                file_path = os.path.join(root_dir, file_name)
                print(f"Processing xml: {file_path}...")

                label_xml(file_path, folder_output)

def main(args):
    # Example usage
    input_path = args.input
    output_path = args.output

    process_all_xml_files(input_path, output_path)

if __name__ == "__main__":
    args = get_arguments()
    main(args)