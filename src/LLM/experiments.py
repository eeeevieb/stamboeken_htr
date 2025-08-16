from groq import Groq
from google import genai
from google.genai import types
import base64
import os
import csv
import time
from lxml import etree
from LLM_src import get_name, get_textline_el, get_prompt_vars, prompt_llama, prompt_gemini

#### Choose which experiments to conduct here, 1 for yes, 0 for no ####

# Experiment 1: Produce full pageXML file including coordinates and region labels using Gemini Flash 2.0
GEMINI_1 = 1

# Experiment 2: Label provided pageXML file containing coordinates useing Gemini Flash 2.0
GEMINI_2 = 0

# Experiment 1: Produce full pageXML file including coordinates and region labels using LLama vision
LLAMA_1 = 0

# Experiment 2: Label provided pageXML file containing coordinates useing Llama vision
LLAMA_2 = 0

# Names of files used
xml_list = [
    "NL-HaNA_2.10.50_1_0005_1.xml",
    "NL-HaNA_2.10.50_1_0005_2.xml",
    "NL-HaNA_2.10.50_1_0006_3.xml",
    "NL-HaNA_2.10.50_1_0007_4.xml",
    "NL-HaNA_2.10.50_1_0007_5.xml",
    "NL-HaNA_2.10.50_1_0008_6.xml",
    "NL-HaNA_2.10.50_1_0014_7.xml",
    "NL-HaNA_2.10.50_1_0015_8.xml",
    "NL-HaNA_2.10.50_1_0017_9.xml",
    "NL-HaNA_2.10.50_1_0018_10.xml",
]

im_list = [
    "NL-HaNA_2.10.50_1_0005_1.JPG",
    "NL-HaNA_2.10.50_1_0005_2.JPG",
    "NL-HaNA_2.10.50_1_0006_3.JPG",
    "NL-HaNA_2.10.50_1_0007_4.JPG",
    "NL-HaNA_2.10.50_1_0007_5.JPG",
    "NL-HaNA_2.10.50_1_0008_6.JPG",
    "NL-HaNA_2.10.50_1_0014_7.JPG",
    "NL-HaNA_2.10.50_1_0015_8.JPG",
    "NL-HaNA_2.10.50_1_0017_9.JPG",
    "NL-HaNA_2.10.50_1_0018_10.JPG",
]

# Prompt for experiment 1
prompt_1 = (
    rf"Attached are two handwritten Dutch pages, \"NL-HaNA_2.10.50_1_0005_0\" and \""
    + "{image}"
    + '".\
                Q: Can you provide me with a PageXML file containing coordinates of text regions, text lines and baselines of "NL-HaNA_2.10.50_1_0005_0", and add labels to the text lines? It can be one of the following labels: Name, Date, Place, Orde. If the text does not fit any label, add label Text. If the text fits more than one label, add both.\
                A: First a header and a page element are created. \
                The first text region encompasses the text "Jonkheer Gerard Godard". \
                The coordinates of this region are 117,232 816,232 816,376 117,376, so a TextRegion element is added with these coordinates.\
                The exact line of text has coordinates 117,237 450,232 458,240 468,237 497,264 516,260 531,245 695,240 739,283 792,287 816,311 816,349 735,353 707,346 619,353 591,376 385,376 371,367 117,368, so a TextLine element is added with these coordinates.\
                The text "Jonkheer Gerard Godard" is a name, so label Name is chosen. Therefore in the custom tag, the text "structure {{type:Name;}}" is added.\
                The coordinates of the baseline are 135,344 185,338 235,337 385,336 799,340, so a Baseline element with these coordinates is added.\
                Then the elements are closed off. The same is done for the other text regions.\
                \
                The full xml file looks like this:'
    + "{input_file}"
    + '\
                \
                Q: Can you provide me with a PageXML file containing coordinates of text regions, text lines and baselines of "'
    + "{image}"
    + '", and add labels to the text lines? It can be one of the following labels: Name, Date, Place, Orde. If the text does not fit any label, add label Text. If the text fits more than one label, add both.'
)

# Prompt for experiment 2
prompt_2 = (
    rf"The following pageXML file contains regions, textlines and baselines of the attached image."
    + "{input_file}"
    + 'This image contains names, geneological data, date of appointment and advancement in the corps, which ship was taken, when and how discharged or died, and specialities.\
                Q: Can you add a label in the form of "structure {{Type:[label];}}" to the custom tag of the TextLine element with id "'
    + "{text_id}"
    + '"? It can be one of the following labels: Name, Date, Place, Orde. If the text does not fit any label, add label Text. If the text fits more than one label, add both.\
                A: This element is located at the first line of the first column of the image. The text is "'
    + "{name}"
    + '". This is a name. Therefore I will add the label Name. The Textline element now looks like this:\
                \
                ```\
                    '
    + "{element}"
    + '\
                ```\
                \
                Q: Can you add a label in the form of "structure {{Type:[label];}}" to the custom tag of the other TextLine elements? It can be one of the following labels: Name, Date, Place, Orde. If the text does not fit any label, add label Text. If the text fits more than one label, add both.\
                Please return only the full labeled pageXML file. Only change the custom tag in the TextLine element, the rest of the pageXML file can stay the same.'
)


if __name__ == "__main__":
    if LLAMA_1 or LLAMA_2:
        llama_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

        if LLAMA_1:
            ## Does not work atm due to Llama accepting only one image ##
            results = [[]]

            # Prompting
            for index, xml in enumerate(xml_list):
                xml_path, im_path, textline_string, textline_id, name = get_prompt_vars(xml, im_list[index])
                results = prompt_llama(
                    llama_client,
                    prompt_1,
                    xml_path,
                    [im_path, "/root/Thesis/stamboeken_htr/experiment_1/stamboeken/NL-HaNA_2.10.50_1_0005_0.JPG"],
                    textline_string,
                    textline_id,
                    name,
                    1,
                )
                print(f"Prompt {index} LLama exp1 done")
                results[0].append(result)
                time.sleep(60)  # Waiting to deal with rate limits

            # Save results
            with open("results/results_Llama_exp1.csv", "w") as f:
                write = csv.writer(f)
                write.writerows(results)

        if LLAMA_2:
            results = [[]]

            # Prompting
            for index, xml in enumerate(xml_list):
                xml_path, im_path, textline_string, textline_id, name = get_prompt_vars(xml, im_list[index])
                result = prompt_llama(llama_client, prompt_2, xml_path, [im_path], textline_string, textline_id, name, 2)
                print(f"Prompt {index} Llama exp2 done")
                results[0].append(result)
                time.sleep(60)  # Waiting to deal with rate limits

            # Save results
            with open("results/results_Llama_exp2.csv", "w") as f:
                write = csv.writer(f)
                write.writerows(results)

    if GEMINI_1 or GEMINI_2:
        gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

        if GEMINI_1:
            results = [[]]

            # Prompting
            for index, xml in enumerate(xml_list):
                xml_path, im_path, textline_string, textline_id, name = get_prompt_vars(xml, im_list[index])
                result = prompt_gemini(
                    gemini_client,
                    prompt_1,
                    xml_path,
                    [im_path, "/root/Thesis/stamboeken_htr/experiment_1/stamboeken/NL-HaNA_2.10.50_1_0005_0.JPG"],
                    textline_string,
                    textline_id,
                    name,
                    1,
                )
                print(f"Prompt {index} Gemini exp1 done")
                results[0].append(result)

            # Save results
            with open("results/results_gemini_exp1.csv", "w") as f:
                write = csv.writer(f)
                write.writerows(results)

        if GEMINI_2:
            results = [[]]

            # Prompting
            for index, xml in enumerate(xml_list):
                xml_path, im_path, textline_string, textline_id, name = get_prompt_vars(xml, im_list[index])
                result = prompt_gemini(gemini_client, prompt_2, xml_path, [im_path], textline_string, textline_id, name, 2)
                print(f"Prompt {index} Gemini exp2 done")

                results[0].append(result)

            # Save results
            with open("results/results_gemini_exp2.csv", "w") as f:
                write = csv.writer(f)
                write.writerows(results)
