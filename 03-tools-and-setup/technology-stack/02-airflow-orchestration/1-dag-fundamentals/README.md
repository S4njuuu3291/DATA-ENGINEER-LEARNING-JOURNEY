# 📊 DAG Fundamentals

Konsep dasar **DAG (Directed Acyclic Graph)** dalam Apache Airflow.

## 🎯 Apa itu DAG?

**DAG** = Directed Acyclic Graph
- **Directed**: Ada arah (task A → task B)
- **Acyclic**: Tidak boleh circular (A → B → A ❌)
- **Graph**: Kumpulan nodes (tasks) dengan edges (dependencies)

### Analogi Sederhana:
Bayangkan bikin kopi:
1. Didihkan air ☕
2. Masukkan kopi bubuk ☕
3. Tuang air panas ☕
4. Aduk ☕

Ini adalah DAG! Setiap step punya urutan, tidak bisa balik.

---

## 📁 Files dalam Folder Ini

1. **1-first-dag.md** - Konsep & teori DAG
2. **2-task-dependencies.py** - Cara bikin dependencies
3. **3-basic-operators.py** - PythonOperator, BashOperator
4. **4-schedule-intervals.py** - Scheduling patterns

---

## 🚀 Quick Example

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# Define functions
def extract():
    print("Extracting data...")
    return "data_extracted"

def transform():
    print("Transforming data...")
    return "data_transformed"

def load():
    print("Loading data...")
    return "data_loaded"

# Define DAG
default_args = {
    'owner': 'data_engineer',
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    dag_id='my_first_etl',
    default_args=default_args,
    description='Simple ETL pipeline',
    schedule='@daily',  # Run every day at midnight
    start_date=datetime(2024, 1, 1),
    catchup=False,  # Don't run for past dates
    tags=['etl', 'example']
) as dag:
    
    # Define tasks
    task_extract = PythonOperator(
        task_id='extract_data',
        python_callable=extract
    )
    
    task_transform = PythonOperator(
        task_id='transform_data',
        python_callable=transform
    )
    
    task_load = PythonOperator(
        task_id='load_data',
        python_callable=load
    )
    
    # Set dependencies
    task_extract >> task_transform >> task_load
```

---

## 📚 Key Concepts

### 1. DAG Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `dag_id` | Unique identifier | `'my_etl_pipeline'` |
| `schedule` | When to run | `'@daily'`, `'0 2 * * *'` |
| `start_date` | First execution date | `datetime(2024, 1, 1)` |
| `catchup` | Run for past dates? | `False` (recommended) |
| `default_args` | Default task settings | `{'retries': 2}` |
| `tags` | Labels for filtering | `['etl', 'production']` |

---

### 2. Schedule Intervals

```python
# Preset schedules
'@once'      # Run once
'@hourly'    # Every hour (0 * * * *)
'@daily'     # Every day at midnight (0 0 * * *)
'@weekly'    # Every Sunday at midnight (0 0 * * 0)
'@monthly'   # First day of month (0 0 1 * *)
'@yearly'    # Jan 1st midnight (0 0 1 1 *)

# Custom cron expressions
'0 2 * * *'    # 2 AM every day
'*/15 * * * *' # Every 15 minutes
'0 9-17 * * 1-5' # 9 AM-5 PM on weekdays
```

**Cron Format:**
```
 ┌───── minute (0 - 59)
 │ ┌───── hour (0 - 23)
 │ │ ┌───── day of month (1 - 31)
 │ │ │ ┌───── month (1 - 12)
 │ │ │ │ ┌───── day of week (0 - 6) (Sunday=0)
 │ │ │ │ │
 * * * * *
```

---

### 3. Task Dependencies

```python
# Method 1: Bitshift operators (recommended)
task1 >> task2 >> task3  # Linear: 1 → 2 → 3

# Method 2: set_downstream
task1.set_downstream(task2)
task2.set_downstream(task3)

# Method 3: set_upstream
task3.set_upstream(task2)
task2.set_upstream(task1)

# Multiple dependencies
task1 >> [task2, task3] >> task4
# task2 and task3 run in parallel after task1
# task4 runs after both complete

# Complex dependencies
task1 >> task2
task1 >> task3
[task2, task3] >> task4
```

---

### 4. Default Args Best Practices

```python
from datetime import datetime, timedelta

default_args = {
    # Ownership
    'owner': 'data_team',
    'email': ['data-alerts@company.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    
    # Retry logic
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(hours=1),
    
    # Timeouts
    'execution_timeout': timedelta(hours=2),
    
    # Dependencies
    'depends_on_past': False,  # Don't wait for previous runs
    'wait_for_downstream': False
}
```

---

## 🎓 Learning Checkpoints

After this folder, you should know:
- ✅ What is a DAG and why it's useful
- ✅ How to create a basic DAG
- ✅ How to set task dependencies
- ✅ How to schedule DAGs
- ✅ Basic operators (PythonOperator, BashOperator)

---

## 🔗 Next Steps

Move to **2-taskflow-api/** untuk modern approach yang lebih clean!
