#Handles the POST action of the STARK DEPLOY POC, but using YAML

#Python Standard Library
import base64
import json
import textwrap
from time import sleep

#Extra modules
import yaml
import boto3
from botocore.exceptions import ClientError

client = boto3.client('cloudformation')

def lambda_handler(event, context):

    isBase64Encoded = event.get('isBase64Encoded', False)
    raw_data_model = event.get('body', '')

    if isBase64Encoded:
        raw_data_model = base64.b64decode(raw_data_model).decode()

    jsonified_payload = json.loads(raw_data_model)
    data_model = yaml.safe_load(jsonified_payload["data_model"])

    project_varname = (data_model.get('__STARK_project_name__')).replace(" ", "_").lower()
    CF_stack_name   = (data_model.get('__STARK_project_name__')).replace(" ", "").lower()

    CF_url = f'https://waynestark-stark-prototype-codegenbucket.s3-ap-southeast-1.amazonaws.com/STARK_SAM_{project_varname}.yaml'

    try:
        response = client.create_stack(
            StackName=CF_stack_name,
            TemplateURL=CF_url,
            TimeoutInMinutes=10,
            Capabilities=[
                'CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM', 'CAPABILITY_AUTO_EXPAND',
            ],
            RoleARN='arn:aws:iam::201649379729:role/STARK_POC_Deploy_CloudFormationServiceRole',
            OnFailure='DELETE',
            EnableTerminationProtection=False
        )

        payload = {
            'status': 'CloudFormation Execution Started',
            'message': "Look at you, testing out next-gen serverless tech! Don't worry, it's coming!",
            'retry': True
        }

    except ClientError as error:
        payload = {
            'status': 'CloudFormation Execution Failed',
            'message': "Sorry, STARK failed to deploy due to an internal error. It's not you, it's us! {" + error.response['Error']['Code'] + "}",
            'retry': False
        }        




    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "body": json.dumps(payload),
        "headers": {
            "Content-Type": "application/json",
        }
    }