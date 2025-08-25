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

        # Add Name label to TextLine element
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
            - the id of first textline element (string)
            - the text of the first textline element (string)
            - the id of the first textline element of the transcript (string)
            - the id text of the first textline element of the transcript (string)
            - the path to the transcript
    """

    xml_path = "../../LLM_experiment_data/empty_xmls_resized/" + xml
    im_path = "../../LLM_experiment_data/stamboeken_resized/" + image
    transcript_path = "../../LLM_experiment_data/stamboeken_resized/fixed/" + xml.strip(".xml") + "_fixed.xml"
    
    textline_string, textline_id = get_textline_el(xml_path)
    name = get_name(transcript_path)
    trans_textline_string, trans_textline_id = get_textline_el(transcript_path)

    return xml_path, im_path, textline_string, textline_id, name, trans_textline_string, trans_textline_id, transcript_path

def prompt_gemini(client, prompt_template, xml, image, textline_string, textline_id, name, exp, image_name):
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
            image_name: the name of the image for region recognition
        
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
        image=image[0],
        image_name=image_name
    )

        # Prompt Gemini
        if exp == 1:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[prompt, image[0], image[1]])
        if exp == 2 or exp == 3:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[prompt, image[0]])
    
    return response.text

# Function to encode the image
def encode_image(image_path):
    """
        Encodes image into base64

        args:
            image_path: path to image to encode

        returns:
            base64 encoded image
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def prompt_llama(client, prompt_template, xml, image, textline_string, textline_id, name, exp, image_name):
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
        image=base64_image,
        image_name=image_name
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
                model="meta-llama/llama-4-maverick-17b-128e-instruct",
            )
        
        if exp == 2 or exp == 3:
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
                model="meta-llama/llama-4-maverick-17b-128e-instruct",
            )

    return chat_completion.choices[0].message.content