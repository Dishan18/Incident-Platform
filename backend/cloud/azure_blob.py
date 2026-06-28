import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

load_dotenv()

CONTAINER_NAME = "rca-files"

def get_container_client(container_name: str = CONTAINER_NAME):
    connection_string = os.getenv(
        "AZURE_STORAGE_CONNECTION_STRING"
    )

    if not connection_string:
        raise ValueError(
            "AZURE_STORAGE_CONNECTION_STRING not found"
        )

    blob_service_client = (
        BlobServiceClient.from_connection_string(
            connection_string
        )
    )

    container_client = blob_service_client.get_container_client(
        container_name
    )

    # Ensure container exists
    try:
        container_client.create_container()
    except Exception:
        # Already exists or failed to create
        pass

    return container_client

def upload_file(file_bytes: bytes, filename: str, container_name: str = CONTAINER_NAME):
    container_client = get_container_client(container_name)

    blob_client = container_client.get_blob_client(
        filename
    )

    blob_client.upload_blob(
        file_bytes,
        overwrite=True
    )

    return filename

def download_file(filename: str, dest_path: str, container_name: str = CONTAINER_NAME):
    container_client = get_container_client(container_name)
    blob_client = container_client.get_blob_client(filename)

    # Ensure local directory exists
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    with open(dest_path, "wb") as f:
        download_stream = blob_client.download_blob()
        f.write(download_stream.readall())

def download_blob_bytes(filename: str, container_name: str = CONTAINER_NAME) -> bytes:
    container_client = get_container_client(container_name)
    blob_client = container_client.get_blob_client(filename)
    download_stream = blob_client.download_blob()
    return download_stream.readall()
