from typing import Any
import os
from lxml import etree
import regex
import csv
import openpyxl
import argparse
import spacy

def get_arguments():
    parser = argparse.ArgumentParser(description="Visualization of regions")

    parser.add_argument("-i", "--input", help="Path to input folder", type=str, default=None)
    parser.add_argument("-o", "--output", help="Path to output folder", type=str)

    args = parser.parse_args()

    return args


def already_labeled(line):
    """
        Checks whether a textline has already been labeled.

        Parameters: 
            - line: the textLine element to be checked
        Output: 
            - a boolean (True if labeled, False if not)
    """
    text = line.get("custom")
    labeled = regex.search(r'structure {type:', text, regex.IGNORECASE)
    if labeled:
        return True
    else:
        return False

def label_line(line, label):
    """
        Labels a TextLine element by adding "structure {type:[label]}" to the custom tag of the TextLine
        Only labels if the line does not have a label yet.

        Parameters:
            - line: the TextLine element to be labeled
            - label: the label that should be used
    """
    if not already_labeled(line):
        new_region = line.get("custom")
        new_region += f" structure {{type:{label};}}"
        line.set("custom", new_region) 
        return   


def label_xml(xml_file, output_file):
    """
        Labels TextLines in an XML file with the following lables:
            - Name          - Marriage Location - Ship
            - Award         - Spouse            - Departure
            - Birth Place   - Children          - Death Date
            - Birth Date    - Rank              - Death Place
            - Father        - Decision          - Retirement
            - Mother        - Appointment       - Date
            - Religion      - Rank date         - Place

        Creates a folder named 'labeled' in given output folder containting the labeled pageXML files.

        Parameters:
        xml_file (file): XML data as a file
        output_file: Name for output file

        Returns:
        XML file: Labeled XML

    """

    ner = spacy.load('nl_core_news_lg') # NL, accuracy
    # ner = spacy.load('nl_core_news_sm') # NL, efficiency
    # ner = spacy.load('xx_sent_ud_sm') # multilang, accuracy
    # ner = spacy.load('xx_ent_wiki_sm') # mulitlang, efficiency

    try:
        tree = etree.parse(xml_file)
        root = tree.getroot()

        new_tree = etree.ElementTree(root)

        result = new_tree.xpath(
            '//ns:TextRegion',
            namespaces={'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}
        )

        if result is None:
            # Log file name if no TextEquiv tag is found
            with open(os.path.join(output_path, "image_htr_error.txt"), "a+") as error_log:
                error_log.write(f"{file_path}\n")
            print(f"No TextEquiv tag found in {file_path}. Logged in image_htr_error.txt.")
            return
            

        for region in result:
            died = False
            rank = False

            text_elements = region.xpath('.//ns:TextEquiv/ns:PlainText', 
                             namespaces={'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})

            # Join all text to check whether the word 'overleden' or a rank is mentioned
            all_text = [el.text for el in text_elements if el.text]
            all_text = ', '.join(all_text)

            overleden_match = regex.search(r'(overleden){e<=2}', all_text, regex.IGNORECASE)
            if overleden_match:
                died = True
            
            rank_match = regex.search(r'\b(lieut|adjudant|maj(?:r|or)|comman|komman|chirurg|inspect|chef|kapit|directeur|klerk|apothek|luit|kolonel){e<=2}', all_text, regex.IGNORECASE)
            if rank_match:
                rank = True

            # Find all TextLines
            text_lines = region.xpath('.//ns:TextLine[ns:TextEquiv[not(ancestor::ns:Word)]]',namespaces={'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})

            for line in text_lines:
                text_equiv_text = line.find("ns:TextEquiv/ns:PlainText", namespaces={
                    'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}).text
                text_coordinates = line.find("ns:Coords", namespaces={
                    'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}).get("points")
                region = line

                if text_equiv_text is None:
                    continue

                # Case 1: Vader
                vader_match = regex.search(r'^(Vader){e<=1}\s+\p{Lu}\w*(?:\s+\w+)*$', text_equiv_text, regex.IGNORECASE)
                if vader_match:
                    label_line(line, 'Father')

                # Case 2: Moeder
                moeder_match = regex.search(r'^(Moeder){e<=1}\s+\p{Lu}\w*(?:\s+\w+)*$', text_equiv_text, regex.IGNORECASE)
                if moeder_match:
                    label_line(line, 'Mother')

                # Case 3: Birth date
                geboorte_datum_match = regex.search(r'^(den (?=.*\b\d{4}\b)\S+(?: \S+)*){e<=1}', text_equiv_text, regex.IGNORECASE)
                if geboorte_datum_match:
                    label_line(line, 'Birth Date')

                # Case 4: Birth place
                geboorte_plaats_match = regex.search(r'^(Geboren){e<=2}\s(te){e<=1}\s+\w+(?:\s+\w+)*$', text_equiv_text)
                if geboorte_plaats_match:
                    label_line(line, 'Birth Place')

                # Case 5: Award (e.g. 'Ridder van de Willems Orde')
                orde_match = regex.search(r'\b(order?|ridder){e<=1}\b', text_equiv_text, regex.IGNORECASE)
                if orde_match:
                    label_line(line, 'Award')
                
                # Case 6: Marriage Location
                marriage_match = regex.search(r'^(Gehuwd){e<=2}\s(te){e<=1}\s+\w+(?:\s+\w+)*$', text_equiv_text, regex.IGNORECASE)
                if marriage_match:
                    label_line(line, 'Marriage Location')

                # Case 7: Spouse
                spouse_match = regex.search(r'^(met){e<=1}\s+(?!\b.*\bschip\b)\p{Lu}\S*.*', text_equiv_text, regex.IGNORECASE)
                if spouse_match:
                    label_line(line, 'Spouse')

                # Case 8: Ship
                ship_match = regex.search(r'^(?!.*welk).*\b(schip)\b{e<=1}.*$', text_equiv_text, regex.IGNORECASE)
                if ship_match:
                    label_line(line, 'Ship')

                # Case 9: Children
                kinderen_match = regex.search(r'^(Kinderen){e<=2}\s+\w+(?:\s+\w+)*$', text_equiv_text, regex.IGNORECASE)
                if kinderen_match:
                    label_line(line, 'Children')

                # Case 10: Decision
                besluit_match = regex.search(r'\b(besl){e<=1}\b', text_equiv_text, regex.IGNORECASE)
                if besluit_match:
                    label_line(line, 'Decision')
                
                # Case 11: Appointment
                aangesteld_match = regex.search(r'(aangest){e<=1}', text_equiv_text, regex.IGNORECASE)
                if aangesteld_match:
                    label_line(line, 'Appointment')

                # Case 12: Death date
                if died:
                    death_date_match = regex.search(r'([0-9]{1,2}\s[A-Z]+[a-z]*\s[1-9]{4}\.*){e<=1}', text_equiv_text, regex.IGNORECASE)
                    if death_date_match:
                        label_line(line, 'Death Date')

                # Case 13: Pensioen
                pensioen_match = regex.search(r'(pensioen){e<=2}', text_equiv_text, regex.IGNORECASE)
                if pensioen_match:
                    label_line(line, 'Retirement')

                # Case 14: Departure
                depart_match = regex.search(r'([0-9]{1,2}\s[A-Z]+[a-z]*[\w\.\'\-]*\s[1-9]{4}\suit\s[A-Z][a-z]*\b){e<=2}', text_equiv_text)
                if depart_match:
                    label_line(line, 'Departure')

                # Case 15: Religion
                religion_match = regex.search(r'^(Godsdienst){e<=3}\s+\w+(?:\s+\w+)*$', text_equiv_text, regex.IGNORECASE)
                if religion_match:
                    label_line(line, 'Religion')

                # Case 16: All dates (full date)
                date_match = regex.search(r'([0-9]{1,2}\s[A-Z]+[a-z]*\s[1-9]{4}\.*){e<=1}', text_equiv_text, regex.IGNORECASE)
                if date_match:
                    if rank:
                        label_line(line, 'Rank Date')
                    if not already_labeled(line):
                        label_line(line, 'Date')

                # Case 17: All dates (only year)
                year_match = regex.search(r'\b1[1-9]{3}\b', text_equiv_text, regex.IGNORECASE)
                if year_match:
                    label_line(line, 'Date')

                # Case 18: Name starting with Baron
                name_match = regex.search(r'(Baron){e<=1}', text_equiv_text, regex.IGNORECASE)
                if name_match:
                    label_line(line, 'Name')

                # Case 19: Rank info
                # One of the later categories to be labeled because it match many words when a few mistakes are permitted
                if rank:
                    function_match = regex.search(r'\b(lieut|adjudant|maj(?:oor|or)|comman|komman|chirurg|inspect|chef|kapit|directeur|klerk|apothek|luit|kolonel){e<=1}', text_equiv_text, regex.IGNORECASE)
                    if function_match:
                        label_line(line, 'Rank')

                # NER
                if not already_labeled(line):
                    doc = ner(text_equiv_text)

                    labels = set()
                    for ent in doc.ents:
                        # Case 20: Name (all names that have not yet been labeled)
                        if ent.label_ == 'PERSON':
                            label_line(line, 'Name')
                        # Places
                        if ent.label_ == 'GPE':
                            # Case 21: Place of death
                            if died:
                                label_line(line, 'Death Place')
                            # Case 22: Place (general)
                            else:
                                label_line(line, 'Place')
                        # Case 23: Date (the dates that are left)
                        if ent.label_ == 'DATE':
                            label_line(line, 'Date')

        # Save file
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