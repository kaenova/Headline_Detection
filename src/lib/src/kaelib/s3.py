# First time i write a code that 90% written by ChatGPT (April 16, 2023) -Kaenova

import os
import warnings
from tqdm import tqdm
from minio import Minio
from minio.error import S3Error

def check_required_env_vars():
    """
    Checks for the presence of required environment variables for upload_folder_to_s3 function.
    If any of the required environment variables are missing, a warning is displayed.

    Returns:
        None
    """
    required_env_vars = ['BUCKET_NAME', 'BUCKET_FOLDER', 'S3_ENDPOINT', 'S3_KEY', 'S3_SECRET', 'S3_REGION', 'S3_USE_SSL']
    missing_env_vars = []

    for env_var in required_env_vars:
        if not os.environ.get(env_var):
            missing_env_vars.append(env_var)

    if missing_env_vars:
        warnings.warn(f"Missing required environment variables: {', '.join(missing_env_vars)}")

def upload_folder_to_s3(folder_path, s3_folder=None, bucket_name=None, s3_endpoint_url=None, access_key=None, secret_key=None, region='default', ssl=False):
    """
    Uploads a folder and its contents to a custom S3 endpoint, with an optional custom folder.

    Args:
        folder_path (str): Path to the local folder to be uploaded.
        s3_folder (str, optional): Custom S3 folder to upload to. Defaults to None.
        bucket_name (str, optional): Custom bucket name. If not provided, it will be retrieved from environment variable BUCKET_NAME. Defaults to None.
        s3_endpoint_url (str, optional): Custom S3 endpoint URL. If not provided, it will be retrieved from environment variable FSSPEC_S3_ENDPOINT_URL. Defaults to None.
        access_key (str, optional): AWS access key. If not provided, it will be retrieved from environment variable FSSPEC_S3_KEY. Defaults to None.
        secret_key (str, optional): AWS secret key. If not provided, it will be retrieved from environment variable FSSPEC_S3_SECRET. Defaults to None.

    Returns:
        None
    """
    # Retrieve environment variables if not provided as function parameters
    if not bucket_name:
        bucket_name = os.environ.get('BUCKET_NAME')
    if not s3_folder:
        s3_folder = os.environ.get('BUCKET_FOLDER')
    if not s3_endpoint_url:
        s3_endpoint_url = os.environ.get('S3_ENDPOINT')
    if not access_key:
        access_key = os.environ.get('S3_KEY')
    if not secret_key:
        secret_key = os.environ.get('S3_SECRET')
    if os.environ.get('S3_REGION') != 'default':
        region = os.environ.get('S3_REGION')
    if os.environ.get("S3_USE_SSL") in ["true", "True", "1"]:
        ssl = True

    s3_client = Minio(s3_endpoint_url,
                      access_key=access_key,
                      secret_key=secret_key,
                      region=region,
                      secure=ssl)

    total_files = sum([len(filenames) for _, _, filenames in os.walk(folder_path)])
    with tqdm(total=total_files, desc="Uploading", unit="file") as progress_bar:
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                local_path = os.path.join(dirpath, filename)
                s3_path = os.path.relpath(local_path, folder_path)

                # Append custom S3 folder to the S3 object key
                if s3_folder:
                    s3_path = os.path.join(s3_folder, s3_path)

                # Convert Windows-style path to Unix-style path
                s3_path = s3_path.replace(os.path.sep, '/')
                local_path = local_path.replace(os.path.sep, '/')

                try:
                    s3_client.fput_object(bucket_name, s3_path, local_path)
                except S3Error as e:
                    print(f"Failed to upload {local_path} to S3: {e}")

                progress_bar.set_postfix(file=os.path.relpath(local_path, folder_path))
                progress_bar.update(1)

    print("Upload complete!")

if __name__ == "__main__":
    pass
    # Example usage:
    # folder_path = "/path/to/folder"
    # s3_folder = "custom-folder"  # Optional: specify a custom S3 folder
    # bucket_name = "my-bucket"  # Optional: specify a custom bucket name
    # s3_endpoint_url = "https://custom.s3.endpoint.com"  # Optional: specify a custom S3 endpoint URL
    # access_key = "my-access-key"  # Optional: specify AWS access key
    # secret_key = "my-secret-key"  # Optional: specify AWS secret key
    # upload_folder_to_s3("tensorboard/fasttext")
