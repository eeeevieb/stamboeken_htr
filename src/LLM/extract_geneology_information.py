import os, csv, ast
from groq import Groq
from lxml import etree


def zero_shot(input_file, description_file):
    root = etree.parse(input_file)

    result = root.xpath(
            '//ns:TextRegion/ns:TextLine[ns:TextEquiv[not(ancestor::ns:Word)]]',
            namespaces={'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}
        )

    if result is None:
        print(f"No TextEquiv tag found in {input_file}. Logged in image_htr_error.txt.")
        return

    results = [line.find("ns:TextEquiv/ns:PlainText", namespaces={
                    'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}).text
               for line in result
               if line is not None]

    response_format = { "type": "json_object" }
    client = Groq()
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {
                "role": "user",
                "content": "Given these list of line segment" + "\n".join([line for line in results if line is not None]) +
                           "extract the information mentioned in this following file" + description_file + ".\
                            Create JSON response. \
                            Do not give me the code, just extract these information. \
                            Just extract the information based on these lines. \
                            If you cannot find the answer, just say information not found."
            }
        ],
        response_format=response_format,
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stop=None,
    )
    return completion.choices[0].message.content


# Walk through all .xml files in the folder
def process_all_xml_files(folder, output_path):
    with open(description_path, 'r') as f:
        description_file = f.read()

    output_file = os.path.join(output_path, 'llm_extracted_information.csv')
    with open(output_file, 'w+') as f:
        csvwriter = csv.writer(f)
        # Write header row
        csvwriter.writerow(["stamboeken", "Achternaam", "Voornaam", "Vader", "Moeder", "Geboorte datum", "Geboorte Plaats"])

    for root_dir, _, files in os.walk(folder):
        for file_name in sorted(files):
            if file_name.endswith(".xml"):
                file_path = os.path.join(root_dir, file_name)
                print(f"Processing xml: {file_path}...")
                try:
                    genealogy_info = ast.literal_eval(zero_shot(file_path, description_file)) # converting json_obj to dict
                except:
                    continue

                try:
                    with open(output_file, 'a') as f:
                        csvwriter = csv.writer(f)
                        csvwriter.writerow(
                            [''.join(file_path.split('/')[-1].split(".")[:-1]),
                             genealogy_info["Achternaam"],
                             genealogy_info["Voornaam"],
                             genealogy_info["Vader"],
                             genealogy_info["Moeder"],
                             genealogy_info["Geboorte datum"],
                             genealogy_info["Geboorte Plaats"],
                             genealogy_info["Laatste Woonplaats"]])
                except:
                    pass

                
                
if __name__=='__main__':
    input_path = '../../stamboek_71/page/NL-HaNA_2.10.50_71_0006.xml'
    description_path = 'information_description.txt'

    with open(description_path, 'r') as f:
            description_file = f.read()

    print("Printing results from ZERO-SHOT: ....\n")

    """
    results = zero_shot(input_path, description_file)
    result_dict = ast.literal_eval(results)
    print(result_dict)
     """

    process_all_xml_files('../../stamboek_71/page', '../../output')

    
