# Upload files under test_files/ to a blob storage account
# Usage: python3 blobuploadtest.py

# create blob service client
from azure.storage.blob import BlobServiceClient
import os
import json

# read markitdown_blobstorage from local.settings.json
with open('local.settings.json') as f:
    data = json.load(f)
    connect_str = data['Values']['markitdown_blobstorage']

# create blob service client
blob_service_client = BlobServiceClient.from_connection_string(connect_str)

# create a container
container_name = 'input'
container_client = blob_service_client.get_container_client(container_name)

# create a blob
# Upload files under test_files/ to a blob storage account
for root, dirs, files in os.walk('test_files'):
    for file in files:
        blob_client = container_client.get_blob_client(file)
        with open(os.path.join(root, file), 'rb') as data:
            blob_client.upload_blob(data, overwrite=True)

print('Upload completed')
