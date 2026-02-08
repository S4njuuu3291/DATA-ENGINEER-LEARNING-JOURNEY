import sys
sys.path.append("/opt/airflow/src")

from airflow.decorators import dag,task
from extract import extract as extract_weather
from transform import transform as transform_weather
from load import load as load_weather
from datetime import datetime


@dag(
    dag_id = 'weather_etl',
    start_date = datetime(2025,10,30),
    schedule_interval = "*/15 * * * *",
    catchup = False
)
def weather_pipeline():
    @task
    def extract():
        return extract_weather()
    
    @task
    def transform(data):
        return transform_weather(data)
    
    @task
    def load(data):
        return load_weather(data)
    
    raw = extract()
    processed = transform(raw)
    load(processed)
    
weather_pipeline()