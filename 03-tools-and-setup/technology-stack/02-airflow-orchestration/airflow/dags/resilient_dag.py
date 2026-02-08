from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta, timezone
from airflow.providers.http.sensors.http import HttpSensor
# from airflow.providers.telegram.hooks.telegram import TelegramHook
from airflow.hooks.base import BaseHook
import requests

def extract():
    conn = BaseHook.get_connection('weather_api')
    url = conn.host + '/v1/forecast?latitude=-6.9&longitude=107.6&current_weather=true'
    response = requests.get(url)
    print(response.text)
    raise Exception("Test Telegram alert")

def send_telegram_alert(context):
    dag_id     = context['dag'].dag_id
    task_id    = context['task_instance'].task_id
    
    utc_time = context['ts']
    utc_dt = datetime.fromisoformat(utc_time.replace("Z", "+00:00"))
    wib_dt = utc_dt + timedelta(hours=7)
    exec_date_wib = wib_dt.strftime("%Y-%m-%d %H:%M:%S") + " WIB"
    
    log_url    = context['task_instance'].log_url
    
    conn = BaseHook.get_connection('telegram_alert')
    token = conn.password
    chat_id = "6147367739"

    message = (
        f"🚨 *Airflow Alert*\n"
        f"• DAG: `{dag_id}`\n"
        f"• Task: `{task_id}`\n"
        f"• Time: `{exec_date_wib}`\n"
        f"🔗 [View Logs]({log_url})"
    )

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode":"Markdown"})

default_args = {
    'retries': 3,
    'retry_delay': timedelta(seconds=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(seconds=20)
}

with DAG(
    dag_id='resilient_dag',
    default_args=default_args,
    start_date=datetime(2025, 1, 1), 
    schedule_interval=None,
    catchup=False,
    on_failure_callback=send_telegram_alert
) as dag:
    
    wait_api = HttpSensor(
        task_id='wait_weather_api',
        http_conn_id='weather_api',
        endpoint='/v1/forecast?latitude=-6.9&longitude=107.6&current_weather=true',
        poke_interval=30,
        timeout=300
    )
    
    extract_task = PythonOperator(
        task_id='extract_from_api',
        python_callable=extract,
    )

    wait_api >> extract_task
