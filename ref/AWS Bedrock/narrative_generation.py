from fastapi import FastAPI
from pydantic import BaseModel
import xml.etree.ElementTree as ET
# from sagemaker.jumpstart.model import JumpStartModel
from dotenv import load_dotenv
from botocore.config import Config
import os
import boto3, json
import uvicorn
# from app.bedrock_details import use_llm_with_aws_bedrock


# app = FastAPI()

# class NarrativeGenInputs(BaseModel):
#     narrative_gen_inputs: dict

def read_xml_file(file_path):
    """
    The function `read_xml_file` reads the contents of an XML file and returns the text.
    
    :param file_path: The file path is the location of the XML file that you want to read. It should be
    a string that specifies the path to the file, including the file name and extension. For example,
    "C:/Users/username/Documents/file.xml" or "data/file.xml"
    :return: The function `read_xml_file` returns the content of the XML file as a string if the file is
    found and can be read successfully. If the file is not found, it returns a string indicating that
    the file was not found at the specified path. If any other error occurs during the file reading
    process, it returns a string indicating that an error occurred, along with the specific error
    message.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as xml_file:
            xml_text = xml_file.read()
            return xml_text
    except FileNotFoundError:
        return f"XML file not found at '{file_path}'"
    except Exception as e:
        return f"An error occurred: {str(e)}"
    

def chunk_xml(xml_string, max_chunk_size, target_tags):
    root = ET.fromstring(xml_string)
    
    current_chunk = ET.Element(root.tag)
    current_chunk_size = 0
    chunks = []

    for element in root.iter():
        if element.tag in target_tags:
            element_str = ET.tostring(element, encoding='utf-8').decode('utf-8')

            # Check if adding the current element exceeds the max_chunk_size
            if current_chunk_size + len(element_str) > max_chunk_size:
                chunks.append(current_chunk)
                current_chunk = ET.Element(root.tag)
                current_chunk_size = 0

            # Append the current element to the current chunk
            current_chunk.append(element)
            current_chunk_size += len(element_str)

    # Append the last chunk if it's not empty
    if len(current_chunk) > 0:
        chunks.append(current_chunk)

    # Create XML strings for each chunk
    # The line `chunk_strings = [ET.tostring(chunk, encoding='utf-8').decode('utf-8') for chunk in
    # chunks]` is creating a list of XML strings for each chunk.
    chunk_strings = [ET.tostring(chunk, encoding='utf-8').decode('utf-8') for chunk in chunks]

    return chunk_strings

def write_chunks_to_files(chunks):
    """
    The function writes each chunk in a list to a separate file in XML format.
    
    :param chunks: The "chunks" parameter is a list of strings, where each string represents a chunk of
    data that needs to be written to a file
    """
    for i, chunk in enumerate(chunks):
        with open(f'./app/data/chunked_xml/output_chunk_{i + 1}.xml', 'w') as file:
            file.write(chunk)


def query_endpoint_with_json_payload(encoded_json, endpoint_name):

    client = boto3.client("runtime.sagemaker")
    response = client.invoke_endpoint(
        EndpointName=endpoint_name, ContentType="application/json", Body=encoded_json, CustomAttributes='accept_eula=true'
    )
    return response

def parse_response_multiple_texts(query_response):

    model_predictions = json.loads(query_response["Body"].read())
    generated_text = model_predictions[0]['generation']["content"]
    return generated_text


# def extract_from_xml(file_path):
#     try:
#         # The code snippet `xml_data = open('xml_data.xml').read()` reads the contents of an XML file named
#         # 'xml_data.xml' and stores it in the variable `xml_data`.
#         # Example usage
#         xml_data = open(file_path).read()
#         max_chunk_size = 4090
#         target_tags = ['patient', 'drug', 'test', 'drugeventmatrix', 'reporter', 'history']
#         chunks = chunk_xml(xml_data, max_chunk_size, target_tags)

#         # Write chunks to XML files
#         write_chunks_to_files(chunks)

#         # Fetch and print the content of each output XML file
#         # The code snippet is iterating over each chunk of XML data and printing the content of each output
#         # XML file.

#         generated_text_list = []
#         for i, chunk in enumerate(chunks):
#             file_path = f'./app/data/chunked_xml/output_chunk_{i + 1}.xml'
#             xml_content = read_xml_file(file_path)
#             if not xml_content.startswith("XML file not found"):
#                 # print(xml_content)
#                 pass
#             else:
#                 # print(xml_content)
#                 pass


#             # prompt= """you are a service similar to Amazon Comprehend Medical that uses machine learning to extract medical information from unstructured text, such as physician notes, discharge summaries, test results, and case notes and I want you to extract following medical entities from given medical narratives
#             # medical Entities to be extracted: reporter, patient, drug, dosage information, test , history, events
#             # Extract all these diseases, drugs, medicines, patients name, past drug, present drug, diahhrea in json format
#             # please extract the medical entities for the below medical narrative and give the output as json same as amazon comprehend medical.
#             # Medical Narrative: """ + xml_content

#             prompt = """
#             [INST] <> 
#             you are a service similar to Amazon Comprehend Medical that uses machine learning to extract medical information from unstructured text, such as physician notes, discharge summaries, test results, and case notes. 
#             <>
#             [SYSTEM PROMPT] <>
#             I want you to extract following medical entities from given medical narratives
#             medical Entities to be extracted: reporter, patient, drug, dosage information, test , history, events
#             Extract all these diseases, drugs, medicines, patients name, past drug, present drug, diahhrea in json format
#             please extract the medical entities for the below medical narrative and give the output as json same as amazon comprehend medical.
#             <>

#             [QUESTION] <>
#             {xml_content}
#             <>
#     """.format(xml_content = xml_content)

#             print(prompt)

#             endpoint_name="meta-textgeneration-llama-2-7b-f-2023-11-09-14-39-45-878"

#             # payload = {
#             #     "inputs": [[
#             #         {"role": "user", "content": prompt},
#             #     ]],
#             #     "parameters": {"max_new_tokens": 4000,  "top_p": 0.7, "temperature": 0.2}
#             # }
#             # query_response = query_endpoint_with_json_payload(
#             #     json.dumps(payload).encode("utf-8"), endpoint_name=endpoint_name
#             # )
#             # generated_texts = parse_response_multiple_texts(query_response)
#             generated_texts = use_llm_with_aws_bedrock(prompt=prompt)
#             generated_text_list.append(generated_texts)
#         print(generated_text_list)
#         return generated_text_list
#     except Exception as e:
#         return repr(e)




def update_prompt(query):
    prompt = f"""
    Act as a  medical reviewer and provide a detailed medical narratives including diagnostic procedures, therapeutic measures taken to treat the patient's condition for the given patient data.
    Patient data includes patient's medical history, treatments, drugs administered, vaccination details, MedDRA codes related to drugs and treatment, adverse event information and reactions.
    Understand the language, context patterns and structure used by medical reviewers when writing Submitted Narative provided in the examples.
    The narrative should be in 500-1800 words and should include all the relevant information from the given query.

    Keys points to include:
    1. Medical terminology: Use specific medical terms and phrases when writing, such as "spinal cord injury", "myocorditis","Multiple sclerosis flare","neuralgia","Instability gait","myalgia","malaise","injection site erythema",”pyrexia”,”hyperpyrexia “,"bacterial infection".
    2. Symptoms and Drug reactions: Describe the symptoms and reactions experienced by the patient, such as "huge rash" , "chest pain", "chills", ”fever",muscular weakness","headache","generalized joint pain" ,"fatigue", "injection site warmth","injection site pain","injection site swelling","injection site inflammation",”nausea”.
    3. Concomitant medications: Mention the concomitant medications taken by the patient, such as "paracetamol ."
    4. Vaccination history: Provide information on the patient's vaccination history, including the type of vaccine, the dose, and the date of administration.
    5. Laboratory results: Include laboratory results in their reports, such as body temperature, white blood cell count, and blood culture,time of vaccination
    6. Medical terminology for medical conditions: Use specific medical terminology when describing medical conditions, such as "COVID-19," "multiple sclerosis," "neuralgia," and "myocorditis."
    7. Patient's Details: Provide patient's age , gender, height and weight to understand potential reactions to the vaccine.
    8. Adverse event terminology: Use adverse event terminology, such as "serious" or "non-serious," to describe the severity of the events reported.
    9. Lot/batch number: Provide the lot/batch number of the vaccine administered to the patient.
    10. Regulatory Number and other case identifiers: provide the Regulatory Number and other case identifiers of the patient.
    11. Drug Information:  Drug strength name,Drug structure dosage unit,drug structure dosage number,drug indication meddra version,drug dosage form.

    Keys points not to include:
    1. Include only actual data available in given query data not the examples data. If enities like drugs, treatment names, age is not available, then do'nt include them.
    2. Dont provide additional notes in the start or at the end like "Based on the input provided" or "Please note that the narrative is written".

    Tasks:
    1. Language Translation: wherever required convert query data which are in  Dutch, Portuguese languages to English .
    2. Provide the "Medical Narrative text" by summarising the key ponits and "narrativeincludeclinical" available in given query.
    3. Provide the output in two to four paragraphs, same format as like Submitted Narative in example output.
    
    Examples:

    {'input:': {'patientweight': 80.0,
   'patientheight': 174,
   'patientsexr3': 2,
   'patientdrugname': 'BioNTech/Pfizer vaccin (Comirnaty)',
   'patientinventedname': 'COVID-19 VACCIN PFIZER INJVLST 0,3ML',
   'primarysrcreactreportedlang': 'nld',
   'primarysrcreactinnativelang': 'De menstruatie was heviger dan normaal',
   'reactionmeddrallt': 10085423,
   'primarysrcreactinnativelang1': None,
   'reactionmeddrallt1': None,
   'testname': 'corona, bevestigd met test',
   'testnamellt': 10084354,
   'testresultcode': 1,
   'medicinalproduct': 'COVID-19 VACCIN PFIZER INJVLST / COVID-19 VACCIN PFIZER INJVLST 0,3ML',
   'druginventedname': 'COVID-19 VACCIN PFIZER INJVLST 0,3ML',
   'drugscientificname': 'COVID-19 VACCIN PFIZER INJVLST',
   'drugindicationprimarysource': 'COVID-19 vaccinatie',
   'drugindicationmeddracode': 10084457,
   'narrativeincludeclinical': 'This spontaneous report from a consumer or other non-health professional concerns a female aged 49 Years, with heavy menstrual bleeding, menstruation prolonged, break through bleeding, postmenopausal bleeding following administration of covid-19 vaccin pfizer injvlst (action taken: not applicable) for covid 19 immunisation. The patient has not recovered from break through bleeding, has not recovered from heavy menstrual bleeding, has not recovered from menstruation prolonged and has not recovered from postmenopausal bleeding.\n\nDrugs and latency: \n1. covid-19 vaccin pfizer injvlst\nheavy menstrual bleeding:  latency unknown\nmenstruation prolonged:  latency unknown\nbreak through bleeding:  latency unknown\npostmenopausal bleeding:  latency unknown\n\n\n\nMedical history : covid 19\nPast drug therapy : covid-19 vaccin pfizer injvlst 0,3ml'},
    'output:': {'Submitted Narative': 'This is a spontaneous report received from a contactable reporter(s) (Consumer or other non HCP) from the European Medicines Agency (EMA) EudraVigilance-WEB. Regulatory number: NL-LRB-00844197 (LRB).\n\nA 49-year-old female patient received BNT162b2 (COMIRNATY), on 06Jul2021 as dose 2, single (Batch/Lot number: unknown) for covid-19 immunisation. The patient\'s relevant medical history was not reported. There were no concomitant medications. Vaccination history included: comirnaty (Dose 1, Single, Strength: 0.3 ml), administration date: 01Jun2021, for covid-19 immunization. The following information was reported: POSTMENOPAUSAL HAEMORRHAGE (medically significant), outcome "not recovered", described as "Vaginal bleeding after menopause: menstruation longer than one year"; HEAVY MENSTRUAL BLEEDING (non-serious), outcome "not recovered", described as "Menstruation was more severe than normal"; INTERMENSTRUAL BLEEDING (non-serious), outcome "not recovered", described as "Break through bleeding". The events "vaginal bleeding after menopause: menstruation longer than one year", "menstruation was more severe than normal" and "break through bleeding" required physician office visit. The patient underwent the following laboratory tests and procedures: Blood test: could not find anything. Diagnostic procedures: Visited the family doctor blood test couldn\'t find anything. Nurse reported that the patient received their infusion on 04Nov2022 of an off label regimen of 500mg every 6 months for the diagnosis of Granulomatosis with Polyangiitis, as per the physician\'s prescription.\n\nNo follow-up attempts are possible; information about lot/batch number cannot be obtained. No further information is expected.'}}
    Provide the Submitted Narative given the input < query:{query} >
    """
    return prompt


def perform_narrative_generation(narrative_gen_inputs):
    try:
        prompt = update_prompt(query=narrative_gen_inputs)
        endpoint_name="meta-textgeneration-llama-2-7b-f-2023-11-09-14-39-45-878"

        payload = {
            "inputs": [[
                {"role": "user", "content": prompt},
            ]],
            "parameters": {"max_new_tokens": 800,  "top_p": 0.7, "temperature": 0.2}
        }
        query_response = query_endpoint_with_json_payload(
            json.dumps(payload).encode("utf-8"), endpoint_name=endpoint_name
        )
        generated_texts = parse_response_multiple_texts(query_response)
        return {'status_code':'200','Message':'Narrative generation successful','response_body':generated_texts}
    except Exception as e:
        return {'status_code':'400','Message':'Narrative generation failed','Error':repr(e)}

