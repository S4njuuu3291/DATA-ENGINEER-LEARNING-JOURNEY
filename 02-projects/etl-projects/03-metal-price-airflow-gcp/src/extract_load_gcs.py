import logging
import requests
from google.cloud import storage
from airflow.hooks.base import BaseHook
from datetime import datetime
import json

def extract_from_api(**context):
    conn = BaseHook.get_connection("metal_dev_api")
    
    base_url = conn.host
    api_key = conn.extra_dejson.get("key")
    url = base_url + "?api_key=" + api_key + "&currency=USD&unit=g"
    
    try:
        logging.info("Starting extract metal price from API")
        response = requests.get(url).json()
        context["ti"].xcom_push(key = "raw_metal_data",value = response)
        logging.info("Completed extract metal price from API")
    except Exception as e:
        logging.error(f"Error during API extraction: {e}")
        raise
    return "Good"

def load_to_gcs(bucket_name,**context):
    raw_data = context["ti"].xcom_pull(key = "raw_metal_data",task_ids = 'extract_from_api')
    today = datetime.now().strftime("%Y-%m-%d: %H-%M")
    dest_path = f"raw/{today}/metal_price.json"
    try:
        filename = f"/tmp/raw_metal_data_{today}.json"
        with open(filename, "w") as f:
            json.dump(raw_data, f)
        logging.info(f"Load data to data lake: {bucket_name}")
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(dest_path)
        blob.upload_from_filename(filename)
        logging.info("Completed load data to data lake")
    except Exception as e:
        logging.error(f"Error during uploading to data lake: {e}")
        raise
    return raw_data