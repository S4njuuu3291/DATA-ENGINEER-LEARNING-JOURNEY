# ⚡ TaskFlow API - Modern Airflow Approach

**TaskFlow API** adalah cara modern untuk menulis DAGs di Airflow 2.0+ dengan syntax yang lebih clean dan Pythonic.

## 🎯 Why TaskFlow API?

### Traditional Approach (Old Way):
```python
def extract():
    return {"data": [1, 2, 3]}

def transform(**context):
    ti = context['ti']
    data = ti.xcom_pull(task_ids='extract')  # Manual XCom pull
    return {"transformed": data}

extract_task = PythonOperator(task_id='extract', python_callable=extract)
transform_task = PythonOperator(task_id='transform', python_callable=transform)

extract_task >> transform_task
```

### TaskFlow API (Modern):
```python
@task
def extract() -> dict:
    return {"data": [1, 2, 3]}

@task
def transform(data: dict) -> dict:  # Auto receives from extract!
    return {"transformed": data}

# Auto dependency & XCom handling!
data = extract()
result = transform(data)
```

## ✅ Benefits:

1. **Less Boilerplate** - No manual XCom push/pull
2. **Type Hints** - Better IDE support & validation
3. **Cleaner Code** - More Pythonic syntax
4. **Auto Dependencies** - Implicit from function calls
5. **Better Testing** - Functions are just functions!

---

## 📁 Files dalam Folder Ini

1. **1-taskflow-intro.md** - Konsep & migration guide (this file)
2. **2-taskflow-vs-traditional.py** - Side-by-side comparison
3. **3-taskflow-etl-complete.py** - Complete ETL example
4. **4-taskflow-advanced.py** - Advanced patterns

---

## 🚀 Quick Start

### Basic Example:

```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(
    dag_id='taskflow_hello',
    schedule='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False
)
def hello_world():
    
    @task
    def say_hello():
        return "Hello from TaskFlow!"
    
    @task
    def print_message(msg: str):
        print(f"Received: {msg}")
    
    # Auto XCom & dependency!
    message = say_hello()
    print_message(message)

# Instantiate the DAG
hello_world()
```

---

## 🔄 Migration from Traditional to TaskFlow

### Before (Traditional):
```python
from airflow import DAG
from airflow.operators.python import PythonOperator

def extract(**context):
    data = [1, 2, 3]
    context['ti'].xcom_push(key='data', value=data)

def transform(**context):
    ti = context['ti']
    data = ti.xcom_pull(key='data', task_ids='extract')
    result = [x * 2 for x in data]
    return result

with DAG('traditional_dag', ...) as dag:
    extract_task = PythonOperator(task_id='extract', python_callable=extract)
    transform_task = PythonOperator(task_id='transform', python_callable=transform)
    extract_task >> transform_task
```

### After (TaskFlow):
```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(dag_id='taskflow_dag', schedule='@daily', start_date=datetime(2024, 1, 1))
def my_pipeline():
    
    @task
    def extract() -> list[int]:
        return [1, 2, 3]
    
    @task
    def transform(data: list[int]) -> list[int]:
        return [x * 2 for x in data]
    
    data = extract()
    transform(data)

my_pipeline()
```

**Changes:**
1. `@dag` decorator instead of `with DAG(...)`
2. `@task` decorator instead of `PythonOperator`
3. Function calls instead of `>>` for dependencies
4. Return values instead of manual XCom
5. Type hints for clarity
6. Must call `my_pipeline()` at the end

---

## 📊 Type Hints Support

TaskFlow API supports automatic serialization for:

```python
from typing import List, Dict, Optional

@task
def extract() -> Dict[str, any]:
    """Returns a dictionary - auto serialized to JSON."""
    return {
        'users': [{'id': 1, 'name': 'Alice'}],
        'count': 1
    }

@task
def transform(data: Dict[str, any]) -> List[dict]:
    """Receives dict, returns list."""
    return data['users']

@task
def load(users: List[dict]) -> Optional[str]:
    """Optional return type."""
    if not users:
        return None
    return f"Loaded {len(users)} users"
```

---

## 🎭 Multiple Outputs

```python
from typing import Tuple

@task
def extract() -> Tuple[list, dict]:
    """Return multiple values."""
    users = [{'id': 1}, {'id': 2}]
    metadata = {'extracted_at': '2024-01-01'}
    return users, metadata

@task
def process_users(users: list):
    print(f"Processing {len(users)} users")

@task
def process_metadata(metadata: dict):
    print(f"Metadata: {metadata}")

# Unpack tuple
users, metadata = extract()
process_users(users)
process_metadata(metadata)
```

---

## 🔗 Mixing TaskFlow with Traditional Operators

You can mix both styles:

```python
from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from datetime import datetime

@dag(dag_id='mixed_dag', schedule='@daily', start_date=datetime(2024, 1, 1))
def mixed_pipeline():
    
    # Traditional operator
    bash_task = BashOperator(
        task_id='bash_task',
        bash_command='echo "Hello from Bash"'
    )
    
    # TaskFlow task
    @task
    def python_task():
        print("Hello from TaskFlow")
        return "data"
    
    @task
    def process(data: str):
        print(f"Processing: {data}")
    
    # Mix dependencies
    bash_task >> python_task()
    data = python_task()
    process(data)

mixed_pipeline()
```

---

## ⚠️ Limitations & Considerations

### 1. XCom Size Limit
```python
# ❌ DON'T: Pass large data via XCom
@task
def bad_extract() -> list:
    return [i for i in range(1_000_000)]  # Too large!

# ✅ DO: Use external storage
@task
def good_extract() -> str:
    large_data = [i for i in range(1_000_000)]
    filepath = '/tmp/data.parquet'
    pd.DataFrame(large_data).to_parquet(filepath)
    return filepath  # Return path, not data
```

### 2. Serialization
Only JSON-serializable types work by default:
```python
# ✅ Works
@task
def returns_simple() -> dict:
    return {'key': 'value'}

# ❌ Doesn't work (custom objects)
@task
def returns_complex() -> MyCustomClass:
    return MyCustomClass()  # Not JSON-serializable

# ✅ Workaround: Use custom XCom backend or convert to dict
```

### 3. Context Access
If you need Airflow context:
```python
@task
def with_context(**context) -> str:
    execution_date = context['execution_date']
    dag_id = context['dag'].dag_id
    return f"Processing {dag_id} at {execution_date}"
```

---

## 🎓 Best Practices

### ✅ DO's:
1. Use type hints always
2. Keep functions pure (testable)
3. Return small data (< 1MB)
4. Use descriptive function names
5. Add docstrings

### ❌ DON'Ts:
1. Don't return large objects
2. Don't use global state
3. Don't mix too many concerns in one task
4. Don't forget to instantiate DAG

---

## 🧪 Testing TaskFlow Tasks

TaskFlow tasks are just functions - easy to test!

```python
# In your DAG file
@task
def process_data(data: list) -> dict:
    return {'count': len(data), 'sum': sum(data)}

# In your test file (test_dags.py)
def test_process_data():
    # TaskFlow tasks are just functions!
    result = process_data.function([1, 2, 3])  # Access underlying function
    assert result == {'count': 3, 'sum': 6}
```

---

## 🔗 Next Steps

1. Check **2-taskflow-vs-traditional.py** - Side-by-side examples
2. Study **3-taskflow-etl-complete.py** - Real ETL pipeline
3. Explore **4-taskflow-advanced.py** - Advanced patterns

**Ready to modernize your DAGs!** ⚡
