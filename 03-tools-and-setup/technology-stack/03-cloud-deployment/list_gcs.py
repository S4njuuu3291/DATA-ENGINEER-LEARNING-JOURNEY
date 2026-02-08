from google.cloud import storage

client = storage.Client()
bucket = client.bucket("weather-data-sanjuds")

print("Files in bucket:")
for blob in client.list_blobs(bucket):
    print(f"- {blob.name}")