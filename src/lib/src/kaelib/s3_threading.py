import os
from minio import Minio
from tqdm import tqdm
import threading
from queue import Queue


def get_all_files_in_directory(directory_path):
    """
    Returns a list of all files in a directory, including its subdirectories, with their full path.

    Args:
        directory_path (str): Path to the directory.

    Returns:
        list: List of all files in the directory with their full path.
    """
    files = []
    for dirpath, _, filenames in os.walk(directory_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            files.append(file_path)
    return files


def upload_folder_to_s3_all_threads(
    folder_path,
    s3_folder=None,
    bucket_name=None,
    s3_endpoint_url=None,
    access_key=None,
    secret_key=None,
    region="default",
    ssl=False,
):
    """
    Uploads a folder and its contents to a custom S3 endpoint, with an optional custom folder, using threading for parallel uploads.
    Skips the upload if a file with the same key already exists in the S3 bucket.

    Args:
        folder_path (str): Path to the local folder to be uploaded.
        s3_folder (str, optional): Custom S3 folder to upload to. Defaults to None.
        bucket_name (str, optional): Custom bucket name. Defaults to None.
        s3_endpoint_url (str, optional): Custom S3 endpoint URL. Defaults to None.
        access_key (str, optional): AWS access key. Defaults to None.
        secret_key (str, optional): AWS secret key. Defaults to None.
        num_threads (int, optional): Number of threads to use for parallel uploads. Defaults to 5.

    Returns:
        None
    """
    # Retrieve environment variables if not provided as function parameters
    bucket_name = bucket_name or os.environ.get("BUCKET_NAME")
    s3_folder = s3_folder or os.environ.get("BUCKET_FOLDER")
    s3_endpoint_url = s3_endpoint_url or os.environ.get("S3_ENDPOINT")
    access_key = access_key or os.environ.get("S3_KEY")
    secret_key = secret_key or os.environ.get("S3_SECRET")
    if os.environ.get("S3_REGION") != "default":
        region = os.environ.get("S3_REGION")
    if os.environ.get("S3_USE_SSL") in ["true", "True", "1"]:
        ssl = True

    s3_client = Minio(
        s3_endpoint_url,
        access_key=access_key,
        secret_key=secret_key,
        region=region,
        secure=ssl,
    )

    files = get_all_files_in_directory(folder_path)
    total_files = len(files)

    def upload_file(folder_path, local_path, s3_folder, progress_bar):
        s3_path = local_path.removeprefix(folder_path)
        # Convert Windows-style path to Unix-style path
        local_path = local_path.replace(os.path.sep, "/")
        s3_path = s3_folder + s3_path.replace(os.path.sep, "/")

        # Check if file exist
        try:
            found = s3_client.stat_object(bucket_name, s3_path)
            if found:
                print(f"Skipping upload of {local_path} as it already exists in S3")
        except:
            try:
                s3_client.fput_object(bucket_name, s3_path, local_path)
            except Exception as e:
                print(f"Failed to upload {local_path} to S3", e)
        progress_bar.set_postfix(file=s3_path)
        progress_bar.update(1)

    progress_bar = tqdm(total=total_files, desc="Uploading", unit="false")
    threads = []
    for file in files:
        t = threading.Thread(
            target=upload_file, args=(folder_path, file, s3_folder, progress_bar)
        )
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print("Upload completed successfully!")


def upload_folder_to_s3_threads_workers(
    folder_path,
    s3_folder=None,
    bucket_name=None,
    s3_endpoint_url=None,
    access_key=None,
    secret_key=None,
    region="default",
    ssl=False,
    num_threads=5,
):
    """
    Uploads a folder and its contents to a custom S3 endpoint, with an optional custom folder, using threading for parallel uploads.
    Skips the upload if a file with the same key already exists in the S3 bucket.

    Args:
        folder_path (str): Path to the local folder to be uploaded.
        s3_folder (str, optional): Custom S3 folder to upload to. Defaults to None.
        bucket_name (str, optional): Custom bucket name. Defaults to None.
        s3_endpoint_url (str, optional): Custom S3 endpoint URL. Defaults to None.
        access_key (str, optional): AWS access key. Defaults to None.
        secret_key (str, optional): AWS secret key. Defaults to None.
        num_threads (int, optional): Number of threads to use for parallel uploads. Defaults to 5.

    Returns:
        None
    """
    # Retrieve environment variables if not provided as function parameters
    bucket_name = bucket_name or os.environ.get("BUCKET_NAME")
    s3_folder = s3_folder or os.environ.get("BUCKET_FOLDER")
    s3_endpoint_url = s3_endpoint_url or os.environ.get("S3_ENDPOINT")
    access_key = access_key or os.environ.get("S3_KEY")
    secret_key = secret_key or os.environ.get("S3_SECRET")
    if os.environ.get("S3_REGION") != "default":
        region = os.environ.get("S3_REGION")
    if os.environ.get("S3_USE_SSL") in ["true", "True", "1"]:
        ssl = True

    s3_client = Minio(
        s3_endpoint_url,
        access_key=access_key,
        secret_key=secret_key,
        region=region,
        secure=ssl,
    )

    files = get_all_files_in_directory(folder_path)
    total_files = len(files)
    files_queue = Queue()

    progress_bar = tqdm(total=total_files, desc="Uploading", unit="file")

    def upload_file(folder_path, local_path, s3_folder):
        s3_path = local_path.removeprefix(folder_path)
        # Convert Windows-style path to Unix-style path
        local_path = local_path.replace(os.path.sep, "/")
        s3_path = s3_folder + s3_path.replace(os.path.sep, "/")

        # Check if file exist
        try:
            found = s3_client.stat_object(bucket_name, s3_path)
            if found:
                print(f"Skipping upload of {local_path} as it already exists in S3")
        except:
            try:
                s3_client.fput_object(bucket_name, s3_path, local_path)
            except Exception as e:
                print(f"Failed to upload {local_path} to S3", e)
        progress_bar.set_postfix(file=s3_path)
        progress_bar.update(1)

    def consumer(queue: "Queue"):
        while not queue.empty():
            current_file = queue.get()
            upload_file(folder_path, current_file, s3_folder)
            queue.task_done()

    for file in files:
        files_queue.put(file)

    consumer_threads = []
    for i in range(num_threads):
        consumer_worker = threading.Thread(target=consumer, args=(files_queue,))
        consumer_worker.start()
        consumer_threads.append(consumer_worker)

    for i in consumer_threads:
        i.join()

    progress_bar.close()
    print("Upload completed successfully!")
