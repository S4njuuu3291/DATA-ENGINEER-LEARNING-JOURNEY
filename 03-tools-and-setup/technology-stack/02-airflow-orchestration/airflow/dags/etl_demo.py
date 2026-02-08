from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import time

def extract():
    print("Extracting data...")
    # raise ValueError("API not reachable!")

def transform():
    print("Transforming data...")

def load():
    print("Loading data to database...")

def notify():
    print("Pipeline success at:", datetime.now())
    
default_args = {
    'owner': 'sanju',
    'retries': 2,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    dag_id='etl_pipeline_demo',
    default_args=default_args,
    description='Simple ETL pipeline demo',
    start_date=datetime(2024, 10, 28),
    schedule_interval=None,
    catchup=False,
) as dag:

    task_extract = PythonOperator(
        task_id='extract_task',
        python_callable=extract
    )

    task_transform = PythonOperator(
        task_id='transform_task',
        python_callable=transform
    )

    task_load = PythonOperator(
        task_id='load_task',
        python_callable=load
    )
    
    task_notify = PythonOperator(
        task_id='notify_task',
        python_callable=notify
    )

    # dependency
    task_extract >> task_transform >> task_load >> task_notify