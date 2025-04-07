import os
import logging
import json

from azure.storage.blob import BlobServiceClient

import dotenv
dotenv.load_dotenv('.env.local')

STORAGE_ACCOUNT_CONNECTION_STRING = os.getenv("STORAGE_ACCOUNT_CONNECTION_STRING")
STORAGE_ACCOUNT_CONTAINER_NAME = os.getenv("STORAGE_ACCOUNT_CONTAINER_NAME")

def load(filename: str) -> list[str]:
    """Load a file from Azure Blob Storage."""
    client = BlobServiceClient.from_connection_string(STORAGE_ACCOUNT_CONNECTION_STRING)

    blob_client = client.get_blob_client(
        container=STORAGE_ACCOUNT_CONTAINER_NAME,
        blob=filename
    )

    downloader = blob_client.download_blob(
        max_concurrency=1,
        encoding='UTF-8'
    )
    blob_text = downloader.readall()

    return blob_text

def save(filename: str, data: str) -> None:
    """Save a file to Azure Blob Storage."""
    client = BlobServiceClient.from_connection_string(STORAGE_ACCOUNT_CONNECTION_STRING)

    blob_client = client.get_blob_client(
        container=STORAGE_ACCOUNT_CONTAINER_NAME,
        blob=filename
    )

    try:
        serialized_data = json.dumps(data)
        blob_client.upload_blob(
            data=serialized_data,
            blob_type="BlockBlob",
            overwrite=True
        )
    except Exception as e:
        logging.error(f"Error uploading blob: {e}")