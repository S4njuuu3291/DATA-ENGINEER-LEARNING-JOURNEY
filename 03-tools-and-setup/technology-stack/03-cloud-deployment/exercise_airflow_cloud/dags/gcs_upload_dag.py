import sys
sys.path.append("/opt/airflow/src")
from airflow.decorators import dag,task
from airflow.operators.python import PythonOperator
from datetime import datetime
from gcs_upload import upload_to_gcs

BUCKET = "weather-data-sanjuds"
SOURCE = "/opt/airflow/data/sample_weather.csv"
DEST = "raw/sample_weather.csv"

@dag(
    dag_id = "upload_to_gcs_dag",
    start_date = datetime(2025,10,30),
    schedule_interval = None,
    catchup = False
)
def weather_cloud():
    @task
    def upload_task(bucket,source,dest):
        return upload_to_gcs(bucket=bucket,source=source,dest=dest)
    
    upload_task(BUCKET,SOURCE,DEST)
    
weather_cloud()