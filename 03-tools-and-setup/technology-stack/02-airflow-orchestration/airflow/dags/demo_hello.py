from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime
with DAG(
    dag_id="demo_hello",
    start_date=datetime(2024, 10, 28),  
    schedule_interval=None,
    catchup=False
) as dag:
    t1 = BashOperator(
        task_id="say_hello",
        bash_command="echo 'Hello from Dockerized Airflow!'"
    )
    