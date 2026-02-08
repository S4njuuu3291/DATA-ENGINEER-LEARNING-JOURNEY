from airflow import DAG
from airflow.models import Variable

def extract():
    endpoint = Variable.get("api_endpoint",default_var= "https://dummy.api/")
    print(f"Fetching data from {endpoint}")
    
from airflow.hooks.base import BaseHook

def load(**context):
    conn = BaseHook.get_connection('postgres_local')
    print("Connected to:", conn.host)
    print("User:", conn.login)

extract()
load()