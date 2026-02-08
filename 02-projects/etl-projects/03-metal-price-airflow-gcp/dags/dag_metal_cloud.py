import sys
sys.path.append("/opt/airflow/src")

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from extract_load_gcs import extract_from_api,load_to_gcs
from transform_data import transform_data
from validate_data import validate_transformed_data
from load_data import load_data
from datetime import datetime, timedelta


default_args = {
    "start_date": datetime(2025,10,6,18,0,0),
    # "retries": 1,
    # "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id = "cloud_metal_price",
    default_args = default_args,
    schedule_interval = "*/30 * * * *",
    catchup = False
):
    extract = PythonOperator(
        task_id = "extract_from_api",
        python_callable = extract_from_api,
        provide_context = True
    )
    
    load_to_lake = PythonOperator(
        task_id = "load_to_gcs",
        python_callable = load_to_gcs,
        op_kwargs = {"bucket_name":"metal_price_raws"},
        provide_context = True
    )
    
    transform = PythonOperator(
        task_id = "transform_data",
        python_callable = transform_data,
        provide_context = True
    )
    
    validate = PythonOperator(
        task_id = "validate_data",
        python_callable = validate_transformed_data,
        provide_context = True
    )
    
    load = PythonOperator(
        task_id = "load_data",
        python_callable = load_data,
        provide_context = True
    )

    extract >> load_to_lake >> transform >> validate >> load
    