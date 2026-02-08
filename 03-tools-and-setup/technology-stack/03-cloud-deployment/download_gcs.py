from google.cloud import storage

def download_from_gcs(bucket_name,blob_name,dest_file):
    client = storage.Client()
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.download_to_filename(dest_file)
    print(f"Downloaded {blob_name} to {dest_file}")

download_from_gcs(
    "weather-data-sanjuds",
    "raw/airtravel_uploaded.csv",
    "data/airtravel_downloaded.csv",
)