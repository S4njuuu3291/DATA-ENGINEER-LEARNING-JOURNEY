import sys
sys.path.append("/opt/airflow/src")

from extract import extract_data
from transform import transform_data
from validate import validate_data
from load import load_data
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

metal = "XAU"
currency = "USD"

default_args = {"start_date": datetime(2025, 1, 1),
                # 'retries': 3,
                # 'retry_delay': timedelta(seconds=5),
                # 'retry_exponential_backoff': True,
                # 'max_retry_delay': timedelta(seconds=20)
                }

with DAG(
    dag_id="metal_price_dags",
    default_args=default_args,
    schedule_interval="0 */6 * * *",
    catchup=False
):
    extract = PythonOperator(
        task_id="extract_task",
        python_callable=extract_data,
        op_kwargs={"metal": metal, "currency": currency},
        provide_context=True
    )

    transform = PythonOperator(
        task_id="transform_task",
        python_callable=transform_data,
        provide_context=True
    )

    validate = PythonOperator(
        task_id="validate_task",
        python_callable=validate_data,
        provide_context=True
    )

    load = PythonOperator(
        task_id="load_task",
        python_callable=load_data,
        provide_context=True
    )

    extract >> transform >> validate >> load