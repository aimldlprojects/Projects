import boto3
import json
import os
from dotenv import load_dotenv



def use_llm_with_aws_bedrock(prompt):
    bedrock_runtime = boto3.client(
        aws_access_key_id= os.getenv('ACCESS_KEY'),
        aws_secret_access_key=os.getenv('SECRET_ACCESS_KEY'),
        service_name='bedrock-runtime', 
        region_name='us-east-1'
    )

    payload = json.dumps({ 
        'prompt': prompt,
        'max_gen_len': 2000,
        'top_p': 0.9,
        'temperature': 0.2
    })

    response = bedrock_runtime.invoke_model(
        body=payload, 
        modelId="meta.llama2-13b-chat-v1", 
        accept='*/*', 
        contentType='application/json'
    )

    body = response.get('body').read().decode('utf-8')
    response_body = json.loads(body)
    # print(response_body['generation'].strip())

    return response_body['generation'].strip()
    
if(__name__=="__main__"):
    load_dotenv()
    use_llm_with_aws_bedrock(prompt="Human: explain black holes to 8th graders")

