# 🚀 Apache Airflow - Workflow Orchestration

Materi lengkap untuk menguasai **Apache Airflow** dalam Data Engineering - dari konsep dasar sampai production-ready practices.

## 🎯 Kenapa Airflow?

Airflow adalah **workflow orchestration tool** yang paling populer di data engineering untuk:
- ✅ Schedule & monitoring ETL/ELT pipelines
- ✅ Manage dependencies antar tasks
- ✅ Retry mechanism otomatis
- ✅ Visualisasi workflow (DAG)
- ✅ Scalable & production-ready

---

## 📚 Learning Path

### 🔴 **CRITICAL: Core Concepts** (Harus dikuasai!)

#### **1. DAG Fundamentals**
Folder: `1-dag-fundamentals/`

**Topics:**
- ✅ DAG (Directed Acyclic Graph) structure
- ✅ Task dependencies (`>>`, `<<`, `set_upstream`, `set_downstream`)
- ✅ Task scheduling & intervals
- ✅ Basic operators (PythonOperator, BashOperator)

**Learn:**
```python
from airflow import DAG
from airflow.operators.python import PythonOperator

with DAG(
    dag_id='my_first_dag',
    schedule='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False
) as dag:
    
    task1 = PythonOperator(task_id='extract', python_callable=extract_data)
    task2 = PythonOperator(task_id='transform', python_callable=transform_data)
    task3 = PythonOperator(task_id='load', python_callable=load_data)
    
    task1 >> task2 >> task3  # Dependencies
```

---

#### **2. TaskFlow API** ⭐ Modern Approach
Folder: `2-taskflow-api/`

**Topics:**
- ✅ `@task` decorator (cleaner syntax)
- ✅ XCom communication (auto return values)
- ✅ Type hints & automatic serialization
- ✅ Error handling dalam tasks

**Learn:**
```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(
    dag_id='taskflow_example',
    schedule='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False
)
def my_etl_pipeline():
    
    @task
    def extract() -> dict:
        """Extract data from API."""
        return {"data": [1, 2, 3]}
    
    @task
    def transform(data: dict) -> dict:
        """Transform data."""
        return {"transformed": data["data"]}
    
    @task
    def load(data: dict):
        """Load to database."""
        print(f"Loading: {data}")
    
    # Auto XCom communication!
    data = extract()
    transformed = transform(data)
    load(transformed)

# Instantiate DAG
my_etl_pipeline()
```

**Why TaskFlow API?**
- ✅ Less boilerplate code
- ✅ Automatic XCom handling
- ✅ Type safety dengan hints
- ✅ Cleaner, more Pythonic

---

#### **3. XCom Communication**
Folder: `3-xcom-patterns/`

**Topics:**
- ✅ Explicit XCom push/pull
- ✅ TaskFlow automatic XCom
- ✅ XCom limitations (size, serialization)
- ✅ Best practices (when to use, when to avoid)

**Explicit XCom:**
```python
def extract(**context):
    data = fetch_api()
    context['ti'].xcom_push(key='raw_data', value=data)

def transform(**context):
    data = context['ti'].xcom_pull(key='raw_data', task_ids='extract_task')
    transformed = process(data)
    return transformed  # Auto push dengan return
```

**TaskFlow XCom (Automatic):**
```python
@task
def extract() -> dict:
    return {"data": [1, 2, 3]}  # Auto XCom push

@task
def transform(data: dict) -> dict:  # Auto XCom pull
    return {"result": data}
```

---

#### **4. Task Scheduling & Retry**
Folder: `4-scheduling-retry/`

**Topics:**
- ✅ Schedule expressions (`@daily`, `@hourly`, cron)
- ✅ Retry mechanisms
- ✅ Exponential backoff
- ✅ Timeout handling
- ✅ SLA & alerting

**Example:**
```python
@dag(
    dag_id='resilient_pipeline',
    schedule='0 2 * * *',  # 2 AM daily
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args={
        'retries': 3,
        'retry_delay': timedelta(minutes=5),
        'retry_exponential_backoff': True,
        'max_retry_delay': timedelta(hours=1),
        'execution_timeout': timedelta(hours=2)
    }
)
def my_dag():
    @task
    def risky_task():
        # Will retry 3x with exponential backoff
        api_call()
```

---

### 🟡 **IMPORTANT: Advanced Topics**

#### **5. Environment Management**
Folder: `5-environment-config/`

**Topics:**
- ✅ Airflow Variables
- ✅ Connections (database, API)
- ✅ Environment variables dalam container
- ✅ Secret management
- ✅ Config separation (dev/prod)

**Using Variables:**
```python
from airflow.models import Variable

@task
def extract():
    api_key = Variable.get("API_KEY")
    api_url = Variable.get("API_URL")
    # Use in requests...
```

**Docker Compose Setup:**
```yaml
services:
  airflow-webserver:
    environment:
      - AIRFLOW_VAR_API_KEY=${API_KEY}
      - AIRFLOW_VAR_DATABASE_URL=${DATABASE_URL}
    env_file:
      - .env
```

---

#### **6. Import Path Resolution**
Folder: `6-import-resolution/`

**Topics:**
- ✅ PYTHONPATH dalam container
- ✅ Custom modules dalam DAGs
- ✅ Shared utilities
- ✅ Package structure best practices

**Project Structure:**
```
airflow/
├── dags/
│   ├── my_dag.py
│   └── utils/          # ❌ Bad: tidak bisa import
│       └── helpers.py
├── plugins/            # ✅ Good: Airflow auto-load
│   └── custom_operators/
└── include/            # ✅ Good: shared code
    └── utils/
        └── helpers.py
```

**Import in DAG:**
```python
# dags/my_dag.py
import sys
from pathlib import Path

# Add include to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'include'))

from utils.helpers import process_data  # Now works!
```

---

#### **7. Custom vs Built-in Operators**
Folder: `7-operators-comparison/`

**Topics:**
- ✅ When to use PythonOperator vs custom
- ✅ Creating custom operators
- ✅ Operator reusability
- ✅ Testing custom operators

**Built-in:**
```python
from airflow.operators.python import PythonOperator

task = PythonOperator(
    task_id='my_task',
    python_callable=my_function
)
```

**Custom Operator:**
```python
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class MyCustomOperator(BaseOperator):
    @apply_defaults
    def __init__(self, my_param, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.my_param = my_param
    
    def execute(self, context):
        # Custom logic
        print(f"Processing {self.my_param}")

# Usage
task = MyCustomOperator(task_id='custom', my_param='value')
```

---

#### **8. Background vs Blocking Tasks**
Folder: `8-task-execution-patterns/`

**Topics:**
- ✅ Synchronous vs asynchronous tasks
- ✅ Sensors for waiting
- ✅ Triggering external processes
- ✅ Deferrable operators

**Blocking (Default):**
```python
@task
def process_large_file():
    # Blocks until complete
    result = heavy_computation()
    return result
```

**Non-blocking (Sensor):**
```python
from airflow.sensors.filesystem import FileSensor

wait_for_file = FileSensor(
    task_id='wait_file',
    filepath='/data/input.csv',
    poke_interval=60,  # Check every 60s
    timeout=3600  # Give up after 1 hour
)
```

---

#### **9. Multi-Container Orchestration**
Folder: `9-docker-compose-setup/`

**Topics:**
- ✅ Airflow + PostgreSQL + Redis
- ✅ Volume mapping untuk DAGs
- ✅ Network configuration
- ✅ Resource limits
- ✅ Development vs Production setup

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow

  redis:
    image: redis:latest

  airflow-webserver:
    image: apache/airflow:2.8.0
    depends_on:
      - postgres
      - redis
    environment:
      AIRFLOW__CORE__EXECUTOR: CeleryExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
      AIRFLOW__CELERY__BROKER_URL: redis://redis:6379/0
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
    ports:
      - "8080:8080"

  airflow-scheduler:
    image: apache/airflow:2.8.0
    depends_on:
      - postgres
      - redis
    environment:
      AIRFLOW__CORE__EXECUTOR: CeleryExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
```

---

## 🎓 Learning Path Recommendations

### Untuk Pemula:
1. Start dengan **DAG Fundamentals** (folder 1)
2. Learn **TaskFlow API** (folder 2) - modern approach
3. Understand **XCom** (folder 3) untuk inter-task communication
4. Practice **Scheduling & Retry** (folder 4)

**Goal:** Bisa bikin basic ETL pipeline dengan Airflow

---

### Untuk Intermediate:
5. Master **Environment Config** (folder 5)
6. Solve **Import Path** issues (folder 6)
7. Learn **Custom Operators** (folder 7)
8. Understand **Task Execution** patterns (folder 8)

**Goal:** Production-ready pipelines dengan proper configuration

---

### Untuk Advanced:
9. Setup **Multi-Container** environment (folder 9)
10. Implement monitoring & alerting
11. Performance optimization
12. CI/CD untuk DAGs

**Goal:** Scalable, maintainable Airflow deployment

---

## 📁 Folder Structure

```
phase3-airflow/
├── README.md (this file)
├── 1-dag-fundamentals/
│   ├── 1-first-dag.md
│   ├── 2-task-dependencies.py
│   ├── 3-basic-operators.py
│   └── README.md
├── 2-taskflow-api/
│   ├── 1-taskflow-intro.md
│   ├── 2-taskflow-vs-traditional.py
│   ├── 3-type-hints-xcom.py
│   └── README.md
├── 3-xcom-patterns/
│   ├── 1-xcom-basics.md
│   ├── 2-explicit-xcom.py
│   ├── 3-taskflow-xcom.py
│   └── README.md
├── 4-scheduling-retry/
│   ├── 1-schedule-expressions.md
│   ├── 2-retry-mechanism.py
│   ├── 3-timeout-handling.py
│   └── README.md
├── 5-environment-config/
│   ├── 1-variables-connections.md
│   ├── 2-docker-env.py
│   ├── 3-secret-management.py
│   └── README.md
├── 6-import-resolution/
│   ├── 1-pythonpath-issues.md
│   ├── 2-project-structure.md
│   ├── 3-import-solutions.py
│   └── README.md
├── 7-operators-comparison/
│   ├── 1-builtin-operators.md
│   ├── 2-custom-operator.py
│   ├── 3-testing-operators.py
│   └── README.md
├── 8-task-execution-patterns/
│   ├── 1-sync-vs-async.md
│   ├── 2-sensors.py
│   ├── 3-deferrable-operators.py
│   └── README.md
└── 9-docker-compose-setup/
    ├── 1-multi-container.md
    ├── docker-compose.yml
    ├── docker-compose.dev.yml
    ├── docker-compose.prod.yml
    └── README.md
```

---

## 🚀 Quick Start

### 1. Basic DAG (Traditional)
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def my_task():
    print("Hello Airflow!")

with DAG(
    dag_id='hello_world',
    schedule='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False
) as dag:
    task = PythonOperator(
        task_id='say_hello',
        python_callable=my_task
    )
```

### 2. Modern DAG (TaskFlow API)
```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(
    dag_id='hello_world_taskflow',
    schedule='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False
)
def hello_pipeline():
    
    @task
    def say_hello():
        print("Hello from TaskFlow!")
        return "Success"
    
    say_hello()

hello_pipeline()
```

---

## 🔗 Integration dengan Tools Lain

### Airflow + Cloud Storage (GCS/S3)
```python
@task
def upload_to_gcs():
    from google.cloud import storage
    client = storage.Client()
    bucket = client.bucket('my-bucket')
    blob = bucket.blob('data.csv')
    blob.upload_from_filename('/tmp/data.csv')
```

### Airflow + dbt
```python
from airflow.operators.bash import BashOperator

dbt_run = BashOperator(
    task_id='dbt_run',
    bash_command='cd /dbt && dbt run --profiles-dir .'
)
```

### Airflow + Spark
```python
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

spark_job = SparkSubmitOperator(
    task_id='spark_transform',
    application='/path/to/spark_job.py',
    conn_id='spark_default'
)
```

---

## 🎯 Best Practices

### ✅ DO's:
- Use **TaskFlow API** untuk DAGs baru
- Implement **retry mechanisms**
- Use **Variables** untuk configuration
- Test DAGs sebelum deploy
- Monitor task duration & failures
- Use **catchup=False** untuk development

### ❌ DON'Ts:
- Jangan hardcode credentials
- Jangan use `depends_on_past=True` tanpa alasan jelas
- Jangan buat tasks terlalu granular (overhead)
- Jangan ignore error handling
- Jangan use XCom untuk large data (use external storage)

---

## 📚 Resources

### Official Docs:
- [Airflow Documentation](https://airflow.apache.org/docs/)
- [TaskFlow API](https://airflow.apache.org/docs/apache-airflow/stable/tutorial/taskflow.html)
- [Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)

### Community:
- [Airflow Slack](https://apache-airflow.slack.com/)
- [GitHub Issues](https://github.com/apache/airflow/issues)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/airflow)

---

## 🎓 Next Steps

Setelah menguasai Airflow:
1. **Phase 4: Cloud** - Deploy Airflow ke GCP/AWS
2. **Phase 5: dbt** - Integrate dengan transformation tool
3. **Phase 6: Kafka** - Real-time data streaming
4. **Phase 7: Spark** - Large-scale data processing

---

**Happy Orchestrating! 🚀**
