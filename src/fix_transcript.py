import argparse
import os
from lxml import etree

def get_arguments():
    parser = argparse.ArgumentParser(description="ASCII characters -1")

    parser.add_argument("-i", "--input", help="Path to transcript", type=str, default=None)

    args = parser.parse_args()

    return args


def fix(xml_path):
    """
    Changes the text in Plaintext and Unicode elements so that the characters are -1 ASCII
    """
    
    try:
        tree = etree.parse(xml_path)
        root = tree.getroot()

        new_tree = etree.ElementTree(root)

        result = new_tree.xpath(
            '//ns:TextEquiv',
            namespaces={'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}
        )

        # Fix PlainText and Unicode elements
        for line in result:
            plain_text = line.find("ns:PlainText", namespaces={
                    'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
            if plain_text.text is not None:
                text = plain_text.text
                new_text = ''.join(chr(ord(c) - 1) for c in text)
                plain_text.text = new_text

            unicode = line.find("ns:Unicode", namespaces={
                    'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
            if unicode.text is not None:
                text = unicode.text
                new_text = ''.join(chr(ord(c) - 1) for c in text)
                unicode.text = new_text
            
        # Save file
        new_path = '/'.join(xml_path.split('/')[:-2])
        new_file = xml_path.split('/')[-1].strip('.xml')
        output_dir = f"{new_path}/fixed"
        os.makedirs(output_dir, exist_ok=True)
        new_tree.write(f"{output_dir}/{new_file}_fixed.xml", pretty_print=True, xml_declaration=True, encoding="UTF-8")

    except etree.XMLSyntaxError:
        print(f"Error parsing {file_path}. File may be malformed.")


def fix_all(folder):
    for root_dir, _, files in os.walk(folder):
        for file_name in sorted(files):
            if file_name.endswith(".xml"):
                file_path = os.path.join(root_dir, file_name)
                print(f"Processing xml: {file_path}...")

                fix(file_path)



if __name__ == "__main__":
    args = get_arguments()
    folder = args.input
    fix_all(folder)
