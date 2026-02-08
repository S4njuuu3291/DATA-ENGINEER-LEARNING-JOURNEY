from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def extract(**context):
    data = {"temp": 29, "city": "Bandung"}
    context['ti'].xcom_push(key = 'weather_data_raw',value = data)
    print("Data extracted:",data)
    
def transform(**context):
    data = context['ti'].xcom_pull(key = 'weather_data_raw',task_ids = 'extract_task')
    data['temp_f'] = data['temp'] *9/5 + 32
    print("Transformed data:",data)
    context['ti'].xcom_push(key = 'weather_data_clean',value= data)
    return data

def load(**context):
    data = context['ti'].xcom_pull(key = 'weather_data_clean',task_ids = 'transform_task')
    print("Final data:",data)
    print("Data siap diload")   
    
    
with DAG(
    dag_id = 'etl_xcom_demo',
    start_date = None,
    schedule_interval = None,
    catchup = False
) as dag:
    
    task_extract = PythonOperator(
        task_id = 'extract_task',
        python_callable = extract,
        provide_context = True
    )
    
    task_transform = PythonOperator(
        task_id = 'transform_task',
        python_callable = transform,
        provide_context = True
    )
    
    task_load = PythonOperator(
        task_id = 'load_task',
        python_callable = load,
        provide_context =  True
    )
    
    task_extract >> task_transform >> task_load