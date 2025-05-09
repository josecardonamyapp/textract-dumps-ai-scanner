import json

import boto3
from textractcaller.t_call import Textract_Features, call_textract
import uuid
from pretty_print_layout import TextractLayoutParser



# radar-put-process-ocr
s3 = boto3.client('s3')

textract_client = boto3.client('textract')

def textract_response_list(textract_json, name):
    blocks = textract_json['Blocks']
    pages_text = []
    current_page_text = "" 
    
    # Procesar los bloques de la primera petición (puede ser la primera página)
    for block in blocks:
        if block["BlockType"] == "LINE":
            try:
                current_page_text += block["Text"] + "\n"
            except KeyError:
                pass
    
    if current_page_text.strip() != "":
        pages_text.append(current_page_text)
    
    response = {
        "response_list": pages_text,
        "Name": name
        
    }
    
    
    return response 

def lambda_handler(event, context):
    document = event['Object']['Name']
    textract_json_form = call_textract(
        input_document= f"s3://ai-scanner-documents-repo-myapp /{document}",
       
        features=[
            Textract_Features.TABLES,
            Textract_Features.LAYOUT,
            Textract_Features.FORMS,
            Textract_Features.SIGNATURES,
        ],
        boto3_textract_client=textract_client
    )
    
    parser = TextractLayoutParser(
        textract_json=textract_json_form,
        table_format="github",
        exclude_figure_text=True,
    )
    

    
    output = parser.get_text()
    json_output = json.dumps(output, indent=4, ensure_ascii=False)
    json_name = 'step1.json'
    bucket_name = 'ai-scanner-documents-repo-myapp '
    
    carpeta = f"data_{uuid.uuid4()}"
    
    s3.put_object(Body=json_output, Bucket = bucket_name, Key= carpeta+'/'+json_name)

    response_response_list = textract_response_list(textract_json_form, document )
    
    return {
        "statusCode": 200,  
        "body": json.dumps({
            "data": json_name, 
            "name": document,
            "bucket": bucket_name,
            "carpeta":carpeta
        }),
         "response_list": response_response_list["response_list"],
         "client": response_response_list["client"],
         "Name": response_response_list["Name"]
    }
    
    
