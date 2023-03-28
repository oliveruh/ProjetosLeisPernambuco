import json
import subprocess


def lambda_handler(event, context):
    subprocess.run(["python", "scrap.py"])
    subprocess.run(["python", "freeze.py"])
    subprocess.run(["python", "s3_upload.py"])
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
