from google.cloud import storage

def upload_to_gcs(bucket,source,dest):
    client = storage.Client()
    bucket = client.bucket(bucket)
    blob = bucket.blob(dest)
    blob.upload_from_filename(source)
    print(f"✅ Uploaded {source} to gs://{bucket.name}/{dest}")