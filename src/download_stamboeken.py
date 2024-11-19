from download_control_book import download_image
import pandas as pd
import re, time, os, requests, openpyxl, json, ast, glob
from lxml import etree
from tqdm import tqdm


def get_downlad_url(content, image_file):
    # Parse the file as XML/HTML
    parser = etree.HTMLParser()
    tree = etree.fromstring(content, parser)

    # Query for the <script> element with type="application/json"
    script_element = tree.xpath('//script[@type="application/json"]')

    # Extract the text content within the tag
    if script_element:
        script_text = script_element[0].text

        # Parse the main JSON string
        json_string = json.loads(script_text)

        # Extract the nested 'view_response' and parse it as JSON
        view_response_str = json_string["na_viewer"]["view_response"]
        view_response = json.loads(view_response_str)

        # Extract 'downloadURI' from the 'files' list for the given image
        download_uris = [file["downloadURI"] for file in view_response["files"] if file["filename"] == image_file]

        return download_uris[0]
    else:
        print("No <script> element with type='application/json' found.")



def download_stamboeken(input_file, output_path):
    start = time.perf_counter()
    with open(input_file, 'rb') as f:
        rows = iter_excel_openpyxl(f)
        for row in tqdm(rows):
            if re.search(r'NL-HaNA_(.*?)_.*?_.*$', row['NA_nummer']) is not None:
                archiveN = re.search(r'NL-HaNA_(.*?)_.*?_.*$', row['NA_nummer']).group(1)
                inv = re.search(r'NL-HaNA_.*?_(.*?)_.*$', row['NA_nummer']).group(1)
                archiveLink = 'https://www.nationaalarchief.nl/onderzoeken/archief/' \
                              + archiveN + '/invnr/' \
                              + inv + '/file/' \
                              + row['NA_nummer'] + "?tab=download"

                response = requests.get(archiveLink, headers={'Content-Type': 'application/xml'})
                if response.status_code == 200:
                    downloadLink = get_downlad_url(response.content, row['NA_nummer'] + ".jpg")
                    print(downloadLink)
                    download_image(downloadLink, str(row['NA_nummer']) + ".jpg", output_path)
            else:
                print(f"Image pattern not found for {row}")


def iter_excel_openpyxl(file):
    workbook = openpyxl.load_workbook(file, read_only=True)
    rows = workbook.active.rows
    headers = [str(cell.value) for cell in next(rows)]
    for row in rows:
        yield dict(zip(headers, (cell.value for cell in row)))


if __name__ == "__main__":
    image_directory = f"../bronbeek_stamboeken"
    if not os.path.exists(image_directory):
        os.makedirs(image_directory)

    download_stamboeken('../Bronbeek_Data/Stamboeken_combined.xlsx', image_directory)
