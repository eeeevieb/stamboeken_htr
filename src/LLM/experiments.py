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

# Experiment 2: Label provided pageXML file containing coordinates using Gemini Flash 2.0
GEMINI_2 = 1

# Experiment 3: Label provided pageXML file containing coordinates and transcript using Gemini Flash 2.0
GEMINI_3 = 1

# Experiment 1: Produce full pageXML file including coordinates and region labels using LLama 4 Maverick
LLAMA_1 = 1

# Experiment 2: Label provided pageXML file containing coordinates using Llama 4 Maverick
LLAMA_2 = 1

# Experiment 3: Label provided pageXML file containing coordinates and transcript using Llama 4 Maverick
LLAMA_3 = 1

# Names of files used
xml_list = ["NL-HaNA_2.10.50_1_0005_1.xml", "NL-HaNA_2.10.50_1_0005_2.xml", "NL-HaNA_2.10.50_1_0006_3.xml", "NL-HaNA_2.10.50_1_0007_4.xml",
            "NL-HaNA_2.10.50_1_0007_5.xml", "NL-HaNA_2.10.50_1_0008_6.xml", "NL-HaNA_2.10.50_1_0014_7.xml", "NL-HaNA_2.10.50_1_0015_8.xml",
            "NL-HaNA_2.10.50_1_0017_9.xml", "NL-HaNA_2.10.50_1_0018_10.xml"]

im_list = ["NL-HaNA_2.10.50_1_0005_1.JPG", "NL-HaNA_2.10.50_1_0005_2.JPG", "NL-HaNA_2.10.50_1_0006_3.JPG", "NL-HaNA_2.10.50_1_0007_4.JPG",
           "NL-HaNA_2.10.50_1_0007_5.JPG", "NL-HaNA_2.10.50_1_0008_6.JPG", "NL-HaNA_2.10.50_1_0014_7.JPG", "NL-HaNA_2.10.50_1_0015_8.JPG",
           "NL-HaNA_2.10.50_1_0017_9.JPG", "NL-HaNA_2.10.50_1_0018_10.JPG"]

# Prompt for experiment 1
prompt_1 = rf"Attached are two handwritten Dutch pages, \"NL-HaNA_2.10.50_1_0005_0\" and \""+"{image_name}"+"\". These images are of stamboeken that contain information about Dutch soldiers. They contain names, genealogical data, date of appointment and advancement in the corps, which ship was taken, when and how discharged or died, and specialties.\
                \
                Q: Can you provide me with a PageXML file containing coordinates of text regions, text lines and baselines of \"NL-HaNA_2.10.50_1_0005_0\", and add labels to the text lines? It can be one of the following labels: Name, Award, Father, Mother, Birth Date, Birth Place, Religion, Marriage Location, Spouse, Children, Rank, Ship, Departure, Retirement, Repatriation, Death Date, Death Place.\
                \
                The labels mean the following:\
                Name: Name of the person whose stamboek this is\
                Award: An award, like ‘Knight of the Order of the Dutch Lion’, or ‘Ridder van de Orde van de Nederlandse Leeuw’\
                Father: Name of father\
                Mother: Name of mother\
                Birth Date: Date of birth\
                Birth Place: Place of birth\
                Religion: Religion\
                Marriage Location: Place where they got married\
                Spouse: Who they got married to\
                Children: This person’s children\
                Rank: The Rank(s) this person has/had\
                Ship: Which ship they took to the Dutch-Indies\
                Departure: Date and place of departure from the Netherlands to the Dutch-Indies\
                Death Date: Date of Death\
                Retirement: Whether and when this person has retired\
                Repatriation: Whether and when this person is repatriated\
                \
                If the text line does not fit any of the categories, do not label it.\
                \
                A: First a header and a page element are created. \
                The first text region encompasses the text \"Jonkheer Gerard Godard\". \
                The coordinates of this region are 47,93 400,93 400,183 47,183, so a TextRegion element is added with these coordinates.\
                The exact line of text has coordinates 47,93 244,97 256,109 336,109 359,132 400,139 400,169 388,172 308,171 288,183 47,178, so a TextLine element is added with these coordinates.\
                The text \"Jonkheer Gerard Godard\" is a name, so label Name is chosen. Therefore in the custom tag, the text \"structure {{type:Name;}}\" is added.\
                The coordinates of the baseline are 62,163 112,158 362,160 386,162, so a Baseline element with these coordinates is added.\
                Then the elements are closed off. The same is done for the other text regions.\
                \
                The full xml file looks like this:"+"{input_file}"+"\
                \
                Q: Can you provide me with a PageXML file containing coordinates of text regions, text lines and baselines of \""+"{image_name}"+"\", and add labels to the text lines? It can be one of the following labels: Name, Award, Father, Mother, Birth Date, Birth Place, Religion, Marriage Location, Spouse, Children, Rank, Ship, Departure, Retirement, Repatriation, Death Date, Death Place. If the text line does not fit any of the categories, do not label it. Please return only the full labeled pageXML file."

# Prompt for experiment 2
prompt_2 = rf"The following pageXML file contains regions, textlines and baselines of the attached image."+ "{input_file}"+ "This image contains names, geneological data, date of appointment and advancement in the corps, which ship was taken, when and how discharged or died, and specialities.\
                The TextLine elements in the PageXML file need to be labeled according to the information they contain. It can be one of the following labels: Name, Award, Father, Mother, Birth Date, Birth Place, Religion, Marriage Location, Spouse, Children, Rank, Ship, Departure, Retirement, Repatriation, Death Date, Death Place.\
                \
                The labels mean the following:\
                Name: Name of the person whose stamboek this is\
                Award: An award, like ‘Knight of the Order of the Dutch Lion’, or ‘Ridder van de Orde van de Nederlandse Leeuw’\
                Father: Name of father\
                Mother: Name of mother\
                Birth Date: Date of birth\
                Birth Place: Place of birth\
                Religion: Religion\
                Marriage Location: Place where they got married\
                Spouse: Who they got married to\
                Children: This person’s children\
                Rank: The Rank(s) this person has/had\
                Ship: Which ship they took to the Dutch-Indies\
                Departure: Date and place of departure from the Netherlands to the Dutch-Indies\
                Death Date: Date of Death\
                Retirement: Whether and when this person has retired\
                Repatriation: Whether and when this person is repatriated\
                \
                Q: Can you add a label in the form of \"structure {{Type:[label];}}\" to the custom tag of the TextLine element with id \""+"{text_id}"+"\"? It can be one of the following labels: Name, Award, Father, Mother, Birth Date, Birth Place, Religion, Marriage Location, Spouse, Children, Rank, Ship, Departure, Retirement, Repatriation, Death Date, Death Place. If the text line does not fit any of the categories, do not label it.\
                A: This element is located at the first line of the first column of the image. The text is \""+"{name}"+"\". This is a name. Therefore I will add the label Name. The Textline element now looks like this:\
                \
                ```\
                    "+"{element}"+"\
                ```\
                \
                Q: Can you add a label in the form of \"structure {{Type:[label];}}\" to the custom tag of the other TextLine elements? It can be one of the following labels: Name, Award, Father, Mother, Birth Date, Birth Place, Religion, Marriage Location, Spouse, Children, Rank, Ship, Departure, Retirement, Repatriation, Death Date, Death Place. If the text line does not fit any of the categories, do not label it. Please return only the full labeled pageXML file. Only change the custom tag in the TextLine element, the rest of the pageXML file can stay the same."

# Prompt for experiment 3
prompt_3 = rf"The following pageXML file contains regions, textlines and baselines of the attached image as well as the transcript of the written words."+"{input_file}"+ "This image is of a stamboek that contains information about Dutch soldiers. They contain names, genealogical data, date of appointment and advancement in the corps, which ship was taken, when and how discharged or died, and specialties.\
                The TextLine elements in the PageXML file need to be labeled according to the information they contain. It can be one of the following labels: Name, Award, Father, Mother, Birth Date, Birth Place, Religion, Marriage Location, Spouse, Children, Rank, Ship, Departure, Retirement, Repatriation, Death Date, Death Place.\
                \
                The labels mean the following:\
                Name: Name of the person whose stamboek this is\
                Award: An award, like ‘Knight of the Order of the Dutch Lion’, or ‘Ridder van de Orde van de Nederlandse Leeuw’\
                Father: Name of father\
                Mother: Name of mother\
                Birth Date: Date of birth\
                Birth Place: Place of birth\
                Religion: Religion\
                Marriage Location: Place where they got married\
                Spouse: Who they got married to\
                Children: This person’s children\
                Rank: The Rank(s) this person has/had\
                Ship: Which ship they took to the Dutch-Indies\
                Departure: Date and place of departure from the Netherlands to the Dutch-Indies\
                Death Date: Date of Death\
                Retirement: Whether and when this person has retired\
                Repatriation: Whether and when this person is repatriated\
                \
                Q: Can you add a label in the form of \"structure {{Type:[label]}};\" to the custom tag of the TextLine element with id"+ "{text_id}"+"? It can be one of the following labels: Name, Award, Father, Mother, Birth Date, Birth Place, Religion, Marriage Location, Spouse, Children, Rank, Ship, Departure, Retirement, Repatriation, Death Date, Death Place. If the text line does not fit any of the categories, do not label it.\
                A: This element is located at the first line of the first column of the image. The text is  \""+"{name}"+"\". This is a name. Therefore I will add the label Name. The Textline element now looks like this:\
                \
                ```\
                    "+"{element}"+"\
                ```\
                \
                Q: Can you add a label in the form of \"structure {{Type:[label];}}\" to the custom tag of the other TextLine elements? It can be one of the following labels: Name, Award, Father, Mother, Birth Date, Birth Place, Religion, Marriage Location, Spouse, Children, Rank, Ship, Departure, Retirement, Repatriation, Death Date, Death Place. If the text line does not fit any of the categories, do not label it. Please return only the full labeled pageXML file. Only change the custom tag in the TextLine element, the rest of the pageXML file can stay the same."

if __name__ == "__main__":
    if LLAMA_1 or LLAMA_2 or LLAMA_3:
        llama_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

        if LLAMA_1:
            results = [[]]

            # Prompting
            for index, xml in enumerate(xml_list):
                xml_path, im_path, textline_string, textline_id, name, trans_textline_string, trans_textline_id, transcript_path = get_prompt_vars(xml, im_list[index])
                result = prompt_llama(llama_client, prompt_1, xml_path, [im_path, '../../LLM_experiment_data/handlabeled_stamboek_resized/NL-HaNA_2.10.50_1_0005_0.JPG'], textline_string, textline_id, name, 1, xml.strip(".xml"))
                print(f"Prompt {index} LLama exp1 done")
                results[0].append(result)
                time.sleep(60)    # Waiting to deal with rate limits
            
            # Save results
            with open('results/results_Llama_exp1.csv', 'w') as f:
                write = csv.writer(f)
                write.writerows(results)

        if LLAMA_2:
            results = [[]]

            # Prompting
            for index, xml in enumerate(xml_list):
                xml_path, im_path, textline_string, textline_id, name, trans_textline_string, trans_textline_id, transcript_path = get_prompt_vars(xml, im_list[index])
                result = prompt_llama(llama_client, prompt_2, xml_path, [im_path], textline_string, textline_id, name, 2, xml.strip(".xml"))
                print(f"Prompt {index} Llama exp2 done")
                results[0].append(result)
                time.sleep(60)    # Waiting to deal with rate limits 

            # Save results
            with open('results/results_Llama_exp2.csv', 'w') as f:
                write = csv.writer(f)
                write.writerows(results)
        
        if LLAMA_3:
            results = [[]]

            # Prompting
            for index, xml in enumerate(xml_list):
                xml_path, im_path, textline_string, textline_id, name, trans_textline_string, trans_textline_id, transcript_path = get_prompt_vars(xml, im_list[index])
                result = prompt_llama(llama_client, prompt_2, transcript_path, [im_path], trans_textline_string, trans_textline_id, name, 3, xml.strip(".xml"))
                print(f"Prompt {index} Llama exp3 done")
                results[0].append(result)
                time.sleep(60)    # Waiting to deal with rate limits 

            # Save results
            with open('results/results_Llama_exp3.csv', 'w') as f:
                write = csv.writer(f)
                write.writerows(results)


    if GEMINI_1 or GEMINI_2 or GEMINI_3:
        gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

        if GEMINI_1:
            results = [[]]

            # Prompting
            for index, xml in enumerate(xml_list):
                xml_path, im_path, textline_string, textline_id, name, trans_textline_string, trans_textline_id, transcript_path = get_prompt_vars(xml, im_list[index])
                result = prompt_gemini(gemini_client, prompt_1,xml_path, [im_path, '../../LLM_experiment_data/handlabeled_stamboek_resized/NL-HaNA_2.10.50_1_0005_0.JPG'], textline_string, textline_id, name, 1, xml.strip(".xml"))
                print(f"Prompt {index} Gemini exp1 done")
                results[0].append(result)

            # Save results           
            with open('results/results_gemini_exp1.csv', 'w') as f:
                write = csv.writer(f)
                write.writerows(results)

        if GEMINI_2:
            results = [[]]

            # Prompting
            for index, xml in enumerate(xml_list):
                xml_path, im_path, textline_string, textline_id, name, trans_textline_string, trans_textline_id, transcript_path = get_prompt_vars(xml, im_list[index])
                result = prompt_gemini(gemini_client, prompt_2, xml_path, [im_path], textline_string, textline_id, name, 2, xml.strip(".xml"))
                print(f"Prompt {index} Gemini exp2 done")

                results[0].append(result)
        
            # Save results
            with open('results/results_gemini_exp2.csv', 'w') as f:
                write = csv.writer(f)
                write.writerows(results)
        
        if GEMINI_3:
            results = [[]]

            # Prompting
            for index, xml in enumerate(xml_list):
                xml_path, im_path, textline_string, textline_id, name, trans_textline_string, trans_textline_id, transcript_path = get_prompt_vars(xml, im_list[index])
                result = prompt_gemini(gemini_client, prompt_2, transcript_path, [im_path], trans_textline_string, trans_textline_id, name, 3, xml.strip(".xml"))
                print(f"Prompt {index} Gemini exp3 done")

                results[0].append(result)
        
            # Save results
            with open('results/results_gemini_exp3.csv', 'w') as f:
                write = csv.writer(f)
                write.writerows(results)
