from lxml import etree
import base64

def get_textline_el(xml_path):
    """
        Returns the first TexLine element with Name label added along with its id

        args:
            xml_path: path to pageXML file the TextLine needs to be extracted from
        
        returns:
            the TextLine element (string) and TextLine id (string)
    """
    try:
        # Load the XML content (from a file)
        root = etree.parse(xml_path)

        # XPath query to get TextLine
        textlines = root.xpath(
            '//ns:TextRegion/ns:TextLine',
            namespaces={'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}
        )

        textline = textlines[0]

        # Add Name label to TextLine elemtn
        new_region = textline.get("custom")
        new_region += " structure {type:Name;}"
        textline.set("custom", new_region)

        # Convert to string
        textline_bytes = etree.tostring(textline)
        textline_string = textline_bytes.decode("utf-8")

        textline_id = textlines[0].get("id")

        if textlines is None:
            # Log file name if no TextEquiv tag is found
            with open(os.path.join(output_path, "image_htr_error.txt"), "a+") as error_log:
                error_log.write(f"{file_path}\n")
            print(f"No TextEquiv tag found in {file_path}. Logged in image_htr_error.txt.")
            return
        
    except etree.XMLSyntaxError:
        print(f"Error parsing {file_path}. File may be malformed.")

    return textline_string, textline_id


def get_name(transcript_path):
    """
        Returns first line of image in XML, which is a name in the images I use.

        args:
            transcript path: path to transcript (XML)

        returns:
            the TextEquiv in first TextLine element (string)
    """
    try:
        # Load the XML content (from a file)
        root = etree.parse(transcript_path)

        # XPath query to get TextEquiv text without nested Word tags
        lines = root.xpath(
            '//ns:TextRegion/ns:TextLine[ns:TextEquiv[not(ancestor::ns:Word)]]',
            namespaces={'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}
        )

        # Get name
        name = text_equiv_text = lines[0].find("ns:TextEquiv/ns:PlainText", namespaces={
                    'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}).text

        if lines is None:
            # Log file name if no TextEquiv tag is found
            with open(os.path.join(output_path, "image_htr_error.txt"), "a+") as error_log:
                error_log.write(f"{file_path}\n")
            print(f"No TextEquiv tag found in {file_path}. Logged in image_htr_error.txt.")
            return

    except etree.XMLSyntaxError:
        print(f"Error parsing {file_path}. File may be malformed.")
    
    return name

def get_prompt_vars(xml, image):
    """
        Returns variables needed in prompts

        args:
            xml: name of XML file that needs to be labeled
            image: name of image that XML corresponds with

        returns: 
            - path to the xml containing only coordinates (string)
            - path to image xml corresponds with (string)
            - the first textline element of XML (string)
            - the textline id of first textline elemnt (string)
            - the text of the first textline element (string)
    """

    xml_path = "/root/Thesis/stamboeken_htr/experiment_2/empty_xmls/" + xml
    im_path = "/root/Thesis/stamboeken_htr/experiment_2/stamboeken/" + image
    transcript_path = "/root/Thesis/stamboeken_htr/experiment_2/xml_transcripts/" + xml.strip(".xml") + "_fixed.xml"
    
    textline_string, textline_id = get_textline_el(xml_path)
    name = get_name(transcript_path)

    return xml_path, im_path, textline_string, textline_id, name

def prompt_gemini(client, prompt_template, xml, image, textline_string, textline_id, name, exp):
    """
        Prompts Gemini Flash 2.0

        args:
            client: the Gemini client
            prompt_template: thte text of the prompt containing variables that still need to be added (string)
            xml: the xml file to be labeled
            image: the image for region recognition
            textline_string: string of the first textline element of xml
            textline_id: id of the first textline element of xml (string)
            name: name/text of first textline element of xml (string)
            exp: 1 for experiment 1 and 2 for experiment 2 (int)
        
        returns:
            response (string)
    """

    with open(xml, 'r') as f:
        input_file = f.read()

        # Fill in prompt
        prompt = prompt_template.format(
        input_file=input_file,
        text_id=textline_id,
        name=name,
        element=textline_string,
        image=image[0]
    )

        # Prompt Gemini
        if exp == 1:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[prompt, image[0], image[1]])
        if exp == 2:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[prompt, image[0]])
    
    return response.text

# Function to encode the image
def encode_image(image_path):
    """
        Encodes image into base64
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def prompt_llama(client, prompt_template, xml, image, textline_string, textline_id, name, exp):
    """
        Prompts Llama 3.2 90B Vision (Preview)

        args:
            client: the Gemini client
            prompt_template: thte text of the prompt containing variables that still need to be added (string)
            xml: the xml file to be labeled
            image: the image for region recognition
            textline_string: string of the first textline element of xml
            textline_id: id of the first textline element of xml (string)
            name: name/text of first textline element of xml (string)
            exp: 1 for experiment 1 and 2 for experiment 2 (int)
        
        returns:
            response (string)
    """

    base64_image = encode_image(image[0])
    
    with open(xml, 'r') as f:
        input_file = f.read()

        # Fill in prompt
        prompt = prompt_template.format(
        input_file=input_file,
        text_id=textline_id,
        name=name,
        element=textline_string,
        image=base64_image
    )

        # Prompt LLama
        if exp == 1:
            base64_image_1 = encode_image(image[1])

            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                },
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image_1}",
                                },
                            },
                        ],
                    }
                ],
                model="llama-3.2-11b-vision-preview",
            )
        
        if exp == 2:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                model="llama-3.2-90b-vision-preview",
            )

    return chat_completion.choices[0].message.content