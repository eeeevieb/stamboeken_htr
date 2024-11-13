import requests, os
import xml.etree.ElementTree as ET
from lxml import etree
from tqdm import tqdm


def download_image(url, image_label, folder):
    try:
        # Send a GET request to the image URL
        response = requests.get(url, stream=True)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Extract the filename from the URL
            # filename = os.path.join(folder, url.split("/")[-1]+".jpg")
            filename = os.path.join(folder, image_label)
            # Save the image to the local file
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Image saved: {filename}")
        else:
            print(f"Failed to download image from {url}. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while downloading the image: {e}")


def send_get_request_and_process_xml(record_url, headers=None):
    namespaces = {
        'oai': 'http://www.openarchives.org/OAI/2.0/',
        'dc': 'http://dublincore.org/documents/dcmi-namespace/',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'mets': 'http://www.loc.gov/METS/',
        'xlink': 'http://www.w3.org/1999/xlink'
    }
    try:
        record_response = requests.get(record_url, headers=headers)

        if record_response.status_code == 200:
            record_root = etree.fromstring(record_response.content)

            # we are interested in Control book 906.
            target = "906"
            # Directory where images will be saved
            image_directory = f"../stamboek_{target}"

            # Create the directory if it does not exist
            if not os.path.exists(image_directory):
                os.makedirs(image_directory)

            xpath_query = f'''//oai:did[
                                oai:unitid[@identifier and text()={target}]
                            ]/oai:dao[@href]'''

            dao_elements = record_root.xpath(xpath_query, namespaces=namespaces)

            for dao in dao_elements:
                control_book_url = dao.attrib['href']

                # Retrieved image from stamboek page-by-page
                try:
                    control_book_response = requests.get(control_book_url, headers=headers)

                    if control_book_response.status_code == 200:
                        control_book_root = etree.fromstring(control_book_response.content)

                        # xpath_query = '//mets:fileGrp[@USE="DEFAULT"]/mets:file/mets:FLocat/@xlink:href'
                        xpath_query1 = '//mets:fileGrp[@USE="DEFAULT"]/mets:file/@ID | ' \
                                                    '//mets:fileGrp[@USE="DEFAULT"]/mets:file/mets:FLocat/@xlink:href '

                        query_results = control_book_root.xpath(xpath_query1, namespaces=namespaces)

                        """Convert consecutive pairs in a list to dictionaries with 'id' and 'href' keys."""
                        dictionary_list = []

                        # Iterate through the list two items at a time
                        for i in range(0, len(query_results), 2):
                            if i + 1 < len(query_results):
                                # Create a dictionary for each pair
                                pair_dict = {
                                    "id": str(query_results[i])[:-3],
                                    "href": query_results[i + 1]
                                }
                                dictionary_list.append(pair_dict)

                        # Print the result
                        for item in tqdm(dictionary_list):
                            print(f"{item['href']}\n")

                            # retrieve correct image label
                            xpath_query2 = f'''//mets:div[@ID="{item['id']}"]/@LABEL'''
                            query_results = control_book_root.xpath(xpath_query2, namespaces=namespaces)
                            # print(query_results)
                            
                            download_image(item['href'], str(query_results[0]).split("/")[-1], image_directory)

                except Exception as e:
                    print(f"An error occurred: {e}")

            """
            # Process specific XML elements (example: print all tags and values)
            print("\nProcessed XML Data:")

            for unitid in record_root.findall('.//oai:unitid[@identifier]', namespaces):
                identifier_value = unitid.attrib['identifier']  # Get the 'identifier' attribute
                unitid_text = unitid.text  # Get the text inside the 'unitid' tag
                # print(f"Identifier: {identifier_value}, UnitID: {unitid_text}")
                print(ET.dump(unitid.findall(".")))

                # Check if identifier text matches any digit 70 to 75
                if unitid_text.isdigit() and 70 <= int(unitid_text) <= 75:
                    print("I AM HERE!")
                    # Search for the sibling 'unitid' with 'audience' attribute and type='handle'
                    # audience_unitid = unitid.find('./oai:following-sibling::oai:unitid[@audience="internal"][@type="handle"]', namespaces)
                    parent_of_unitid = unitid.getroot()
                    audience_unitid = parent_of_unitid.find('.//oai:unitid[@audience="internal"][@type="handle"]]',
                                                            namespaces)
                    # audience_unitid = unitid.itersiblings()

                    if audience_unitid is not None:
                        audience_value = unitid.text  # Get the text of the audience unitid
                        print(f"Identifier: {identifier_value}, UnitID: {unitid_text}, Audience: {audience_value}")
        

        else:
            print(f"Request failed with status code: {response.status_code}")
            print(f"Error response: {response.text}")
"""
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    # url = 'https://service.archief.nl/gaf/oai/!open_oai.OAIHandler?verb=ListRecords&set=2.10.50&metadataPrefix=oai_ead'
    url = "https://service.archief.nl/gaf/oai/!open_oai.OAIHandler?verb=ListRecords&set=2.10.36.22&metadataPrefix=oai_ead"

    headers = {
        'Content-Type': 'application/xml',
    }
    send_get_request_and_process_xml(url, headers=headers)
