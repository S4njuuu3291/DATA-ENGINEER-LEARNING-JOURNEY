from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from airflow.hooks.base import BaseHook
from datetime import datetime

def extract(**context):
    endpoint = Variable.get('api_endpoint')
    print("Extracting data from",endpoint)
    
def load(**context):
    conn = BaseHook.get_connection('postgres_local')
    print(f"Loading data into {conn.host}:{conn.port}/{conn.schema}")
    
with DAG (
    dag_id = 'etl_var_connect_demo',
    start_date= None,
    schedule_interval = None,
    catchup = False
) as dag:
    task_extract = PythonOperator(
        task_id = 'extract_data',
        python_callable = extract
    )
    
    task_load = PythonOperator(
        task_id = 'load_data',
        python_callable = load
    )
    
    task_extract >> task_load
