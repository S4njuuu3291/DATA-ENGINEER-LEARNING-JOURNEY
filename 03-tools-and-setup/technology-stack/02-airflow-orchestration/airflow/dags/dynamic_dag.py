from airflow.decorators import dag,task
from datetime import datetime

@dag (
    dag_id = 'taskflow_example',
    start_date = datetime(2025,10,10),
    schedule_interval = None,
    catchup = False
)
def my_dag():
    @task
    def extract():
        return {'city':'Bandung','temp':29}
    
    @task
    def transform(data):
        data['temp_f'] = data['temp']*9/5 + 32
        return data
    
    @task
    def load(data):
        print("Loaded:",data)
        
    load(transform(extract()))

cities = ["Bandung", "Jakarta", "Surabaya"]

@dag(
    dag_id="dynamic_etl",
    start_date=datetime(2025,11,17),
    schedule_interval=None,
    catchup=False
)
def dynamic_dag():

    @task
    def extract(city):
        print(f"Extract {city}")
        return city

    @task
    def transform(city):
        print(f"Transform {city}")
        return city.upper()

    @task
    def load(city):
        print(f"Load {city}")

    city_tasks = extract.expand(city=cities)
    transformed = transform.expand(city=city_tasks)
    load.expand(city=transformed)

my_dag()
dynamic_dag()
