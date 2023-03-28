import os
import sys
import boto3
import hashlib
from app import create_app
import logging

# Setting up logging
logging.basicConfig(level=logging.NOTSET)
log = logging.getLogger(__name__)

# Setting up app context
app = create_app()

# get an access token, local (from) directory, and S3 (to) directory
# from the command-line
local_directory = sys.argv[1:2]

local_directory = local_directory[0]

client = boto3.client('s3', aws_access_key_id=app.config['AWS_ACCESS_KEY'], aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'])
bucket = app.config['S3_BUCKET']

# enumerate local files recursively
for root, dirs, files in os.walk(local_directory):

  for filename in files:

    # construct the full local path
    local_path = os.path.join(root, filename)

    # construct the full Dropbox path
    relative_path = os.path.relpath(local_path, local_directory)
    s3_key = os.path.join(relative_path).replace("\\", "/")

    # get the MD5 hash of the local file
    with open(local_path, 'rb') as f:
        local_md5 = hashlib.md5(f.read()).hexdigest()

    log.info( 'Searching "%s" in "%s"' % (s3_key, bucket))
    try:
        s3_object = client.head_object(Bucket=bucket, Key=s3_key)
        log.info( "Path found on S3! Skipping %s..." % s3_key)

        # get the MD5 hash of the S3 object
        s3_md5 = s3_object['ETag'].strip('"')

        if local_md5 != s3_md5:
            log.info(f"Updating {local_path} to {bucket}/{s3_key}...")
            # upload the file to S3
            if (s3_key.split('.')[1] == 'html'):
                client.upload_file(local_path, bucket, s3_key, ExtraArgs={'ContentType': "text/html"})
            elif (s3_key.split('.')[1] == 'css'):
                client.upload_file(local_path, bucket, s3_key, ExtraArgs={'ContentType': "text/css"})
            elif (s3_key.split('.')[1] == 'json'):
                client.upload_file(local_path, bucket, s3_key, ExtraArgs={'ContentType': "application/json"})
            elif (s3_key.split('.')[1] == 'xml'):
                client.upload_file(local_path, bucket, s3_key, ExtraArgs={'ContentType': "application/xml"})
            elif (s3_key.split('.')[1] == 'txt'):
                client.upload_file(local_path, bucket, s3_key, ExtraArgs={'ContentType': "text/plain"})
            else:
                client.upload_file(local_path, bucket, s3_key)
        else:
            log.info(f"{local_path} already exists in S3 and has not been modified.")

    except:
        log.info( "Uploading %s..." % s3_key)
        if (s3_key.split('.')[1] == 'html'):
            client.upload_file(local_path, bucket, s3_key, ExtraArgs={'ContentType': "text/html"})
        elif (s3_key.split('.')[1] == 'css'):
            client.upload_file(local_path, bucket, s3_key, ExtraArgs={'ContentType': "text/css"})
        elif (s3_key.split('.')[1] == 'json'):
            client.upload_file(local_path, bucket, s3_key, ExtraArgs={'ContentType': "application/json"})
        else:
            client.upload_file(local_path, bucket, s3_key)