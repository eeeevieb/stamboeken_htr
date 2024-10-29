import os
from lxml import etree
import re
import csv


# Function to process each XML file
def extract_textequiv(file_path):
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
            return

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


def extract_genealogy_information(xml_file):
    """
        Extracts genealogy information, i.e.,:
            - Vader (father)
            - Moeder (mother)
            - Geboorte datum (birth date)
            - Geboorte Plaats (birthplace)
            - Laatste Woonplaats (last residence)
        from the XML content based on different cases.

        Parameters:
        xml_file (file): XML data as a file

        Returns:
        dict: Extracted genealogy information.
    """

    try:
        root = etree.parse(xml_file)

        result = root.xpath(
            '//ns:TextRegion/ns:TextLine[ns:TextEquiv[not(ancestor::ns:Word)]]',
            namespaces={'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}
        )

        if result is None:
            # Log file name if no TextEquiv tag is found
            with open(os.path.join(output_path, "image_htr_error.txt"), "a+") as error_log:
                error_log.write(f"{file_path}\n")
            print(f"No TextEquiv tag found in {file_path}. Logged in image_htr_error.txt.")
            return

        # WHEN HTR DONE SUCCESSFULLY!
        genealogy_info = {
            "Vader": None,
            "Moeder": None,
            "Geboorte datum": None,
            "Geboorte Plaats": None,
            "Laatste Woonplaats": None
        }

        # Extract and print the required information
        for line in result:
            text_region_id = line.getparent().get("id")
            text_line_id = line.get("id")
            text_equiv_text = line.find("ns:TextEquiv/ns:PlainText", namespaces={
                'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}).text

            if text_equiv_text is None:
                continue

            # Case 1: Extract Vader
            vader_match = re.search(r'.*Vader\s+(.+)', text_equiv_text, re.IGNORECASE)
            if vader_match:
                genealogy_info["Vader"] = vader_match.group(1).strip()

            # Case 2: Extract Moeder
            moeder_match = re.search(r'.*Moeder\s+(.+)', text_equiv_text, re.IGNORECASE)
            if moeder_match:
                genealogy_info["Moeder"] = moeder_match.group(1).strip()

            # Case 3: Extract Geboorte datum (e.g., "Geboren: 01-01-1900")
            geboorte_datum_match = re.search(r'Geboren\s+(.+)', text_equiv_text, re.IGNORECASE)
            if geboorte_datum_match:
                genealogy_info["Geboorte datum"] = geboorte_datum_match.group(1).strip()

            # Case 4: Extract Geboorte Plaats (e.g., "te Amsterdam")
            geboorte_plaats_match = re.search(r'^te\s+(.+)', text_equiv_text, re.IGNORECASE)
            if geboorte_plaats_match:
                if genealogy_info["Geboorte Plaats"] is None:
                    genealogy_info["Geboorte Plaats"] = geboorte_plaats_match.group(1).strip()

            # Case 5: Extract Laatste Woonplaats (e.g., "laatst gewoond te Rotterdam")
            laatste_woonplaats_match = re.search(r'laatst\s*gewoond te\s+(.+)', text_equiv_text, re.IGNORECASE)
            if laatste_woonplaats_match:
                genealogy_info["Laatste Woonplaats"] = laatste_woonplaats_match.group(1).strip()

        return genealogy_info

    except etree.XMLSyntaxError:
        print(f"Error parsing {file_path}. File may be malformed.")


def extract_campaign_information():
    """
    TODO: Extract  campaigns (LAST COLUMN)
    """
    pass


def extract_military_posting_information():
    """
    TODO: Extract  campaigns (LAST COLUMN)
    """
    pass


# Walk through all .xml files in the folder
def process_all_xml_files(folder):
    for root_dir, _, files in os.walk(folder):
        for file_name in sorted(files):
            if file_name.endswith(".xml"):
                file_path = os.path.join(root_dir, file_name)
                print(f"Processing xml: {file_path}...\n")
                extract_textequiv(file_path)


# Example usage
input_path = "image_samples/page"
output_path = 'output'
# process_all_xml_files(input_path)
print(extract_genealogy_information("image_samples/page/NL-HaNA_2.10.50_71_0006.xml")) # perfect exmaple NL-HaNA_2.10.50_71_0006.xml
