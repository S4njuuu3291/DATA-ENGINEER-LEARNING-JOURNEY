"""
BASIC OPERATORS - Industry Standard Patterns

Topics:
- PythonOperator (most common)
- BashOperator
- EmailOperator (notifications)
- Task context & templating

Production patterns untuk daily use.

Copy to: airflow/dags/
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.email import EmailOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
import logging

# Setup logger
logger = logging.getLogger(__name__)

# ==========================================
# PYTHONOPERATOR - Most Common
# ==========================================

def extract_data(**context):
    """
    Extract data function dengan context.
    
    **context gives access to:
    - execution_date
    - task_instance (ti)
    - dag
    - params
    """
    execution_date = context['execution_date']
    logger.info(f"Extracting data for {execution_date}")
    
    # Simulate API call
    data = {
        'users': [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'}
        ],
        'extracted_at': str(execution_date)
    }
    
    logger.info(f"Extracted {len(data['users'])} users")
    return data

def transform_data(data):
    """
    Transform data - can receive params directly.
    """
    logger.info("Transforming data...")
    
    # Add computed field
    for user in data['users']:
        user['name_upper'] = user['name'].upper()
    
    return data

def load_data(**context):
    """
    Load data using context to pull from XCom.
    """
    ti = context['ti']
    
    # Pull from previous task
    data = ti.xcom_pull(task_ids='extract')
    
    logger.info(f"Loading {len(data['users'])} records")
    # Simulate database insert
    print("Data loaded to database:")
    print(data)

# ==========================================
# DAG 1: PYTHONOPERATOR BASIC
# ==========================================

with DAG(
    dag_id='basic_python_operator',
    description='Basic PythonOperator usage',
    schedule='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['example', 'python']
) as dag1:
    
    extract = PythonOperator(
        task_id='extract',
        python_callable=extract_data,
        provide_context=True  # Pass **context to function
    )
    
    transform = PythonOperator(
        task_id='transform',
        python_callable=transform_data,
        op_args=[],  # Positional args
        op_kwargs={}  # Keyword args
    )
    
    load = PythonOperator(
        task_id='load',
        python_callable=load_data,
        provide_context=True
    )
    
    extract >> transform >> load

# ==========================================
# BASHOPERATOR - Shell Commands
# ==========================================

with DAG(
    dag_id='basic_bash_operator',
    description='Basic BashOperator usage',
    schedule='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['example', 'bash']
) as dag2:
    
    # Simple bash command
    check_disk_space = BashOperator(
        task_id='check_disk_space',
        bash_command='df -h'
    )
    
    # Multi-line bash script
    create_directory = BashOperator(
        task_id='create_directory',
        bash_command='''
            mkdir -p /tmp/airflow_data
            echo "Directory created at $(date)" > /tmp/airflow_data/timestamp.txt
            ls -la /tmp/airflow_data/
        '''
    )
    
    # Bash with environment variables
    process_file = BashOperator(
        task_id='process_file',
        bash_command='echo "Processing for {{ ds }}"',  # Jinja template
        env={
            'DATA_PATH': '/tmp/airflow_data',
            'ENV': 'production'
        }
    )
    
    # Chain multiple bash commands
    cleanup = BashOperator(
        task_id='cleanup',
        bash_command='''
            echo "Cleaning up old files..."
            find /tmp/airflow_data -type f -mtime +7 -delete
            echo "Cleanup completed"
        '''
    )
    
    check_disk_space >> create_directory >> process_file >> cleanup

# ==========================================
# JINJA TEMPLATING - Dynamic Values
# ==========================================

def process_date(**context):
    """Access templated values."""
    ds = context['ds']  # Execution date as string (YYYY-MM-DD)
    ds_nodash = context['ds_nodash']  # YYYYMMDD
    execution_date = context['execution_date']
    
    logger.info(f"Processing date: {ds}")
    logger.info(f"No dash: {ds_nodash}")
    logger.info(f"Full datetime: {execution_date}")
    
    return {
        'date': ds,
        'date_nodash': ds_nodash
    }

with DAG(
    dag_id='templating_example',
    description='Jinja templating dengan Airflow macros',
    schedule='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['example', 'templating']
) as dag3:
    
    # Jinja in BashOperator
    templated_bash = BashOperator(
        task_id='templated_bash',
        bash_command='''
            echo "Execution date: {{ ds }}"
            echo "Previous date: {{ prev_ds }}"
            echo "Next date: {{ next_ds }}"
            echo "DAG ID: {{ dag.dag_id }}"
            echo "Task ID: {{ task.task_id }}"
        '''
    )
    
    # Access in Python
    templated_python = PythonOperator(
        task_id='templated_python',
        python_callable=process_date
    )
    
    templated_bash >> templated_python

# ==========================================
# OPERATOR WITH RETRY & TIMEOUT
# ==========================================

def risky_operation():
    """Operation that might fail."""
    import random
    
    if random.random() < 0.3:  # 30% chance of failure
        raise Exception("Random failure!")
    
    logger.info("Operation succeeded!")
    return "Success"

with DAG(
    dag_id='retry_timeout_example',
    description='Retry & timeout configuration',
    schedule='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['example', 'resilience']
) as dag4:
    
    risky_task = PythonOperator(
        task_id='risky_task',
        python_callable=risky_operation,
        retries=3,  # Override default
        retry_delay=timedelta(minutes=2),
        retry_exponential_backoff=True,
        max_retry_delay=timedelta(minutes=10),
        execution_timeout=timedelta(minutes=5)
    )
    
    # Bash command dengan timeout
    long_running_bash = BashOperator(
        task_id='long_running',
        bash_command='sleep 2 && echo "Completed"',
        execution_timeout=timedelta(seconds=10)  # Will succeed
    )
    
    risky_task >> long_running_bash

# ==========================================
# CONDITIONAL EXECUTION
# ==========================================

def check_condition(**context):
    """Check if we should continue."""
    import random
    should_continue = random.choice([True, False])
    
    logger.info(f"Condition: {should_continue}")
    
    if not should_continue:
        raise ValueError("Condition not met, skipping downstream")
    
    return "continue"

def conditional_task():
    """Only runs if condition is True."""
    logger.info("Conditional task executed!")

with DAG(
    dag_id='conditional_execution',
    description='Conditional task execution',
    schedule='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['example', 'conditional']
) as dag5:
    
    check = PythonOperator(
        task_id='check_condition',
        python_callable=check_condition
    )
    
    execute = PythonOperator(
        task_id='conditional_task',
        python_callable=conditional_task
    )
    
    check >> execute

# ==========================================
# PASSING ARGUMENTS TO OPERATORS
# ==========================================

def greet(name, message="Hello"):
    """Function dengan parameters."""
    print(f"{message}, {name}!")
    return f"{message}, {name}!"

def calculate(a, b, operation='add'):
    """Function dengan multiple params."""
    if operation == 'add':
        result = a + b
    elif operation == 'multiply':
        result = a * b
    else:
        result = 0
    
    print(f"{a} {operation} {b} = {result}")
    return result

with DAG(
    dag_id='operator_arguments',
    description='Passing arguments to operators',
    schedule='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['example', 'arguments']
) as dag6:
    
    # op_args: positional arguments
    greet_task = PythonOperator(
        task_id='greet',
        python_callable=greet,
        op_args=['World'],  # name='World'
        op_kwargs={'message': 'Hi'}  # message='Hi'
    )
    
    # op_kwargs: keyword arguments
    calculate_task = PythonOperator(
        task_id='calculate',
        python_callable=calculate,
        op_kwargs={
            'a': 10,
            'b': 5,
            'operation': 'multiply'
        }
    )
    
    greet_task >> calculate_task

# ==========================================
# BEST PRACTICES SUMMARY
# ==========================================

"""
✅ PythonOperator Best Practices:

1. Use **context when you need Airflow metadata
2. Keep functions pure & testable (avoid side effects)
3. Return values for XCom (small data only!)
4. Use logging instead of print
5. Handle exceptions gracefully

✅ BashOperator Best Practices:

1. Use for simple shell commands
2. Avoid complex bash scripts (use Python instead)
3. Use Jinja templates untuk dynamic values
4. Set proper environment variables
5. Always check exit codes

✅ General Operator Tips:

1. Set appropriate retries & timeouts
2. Use descriptive task_ids
3. Tag DAGs untuk easy filtering
4. Test operators individually before combining
5. Monitor task duration untuk optimization

❌ Common Mistakes:

1. Don't pass large data via XCom (use external storage)
2. Don't hardcode dates (use Jinja templates)
3. Don't ignore error handling
4. Don't mix too many operator types in one DAG
5. Don't forget to set execution_timeout

📚 Available Macros:

{{ ds }}              # Execution date (YYYY-MM-DD)
{{ ds_nodash }}       # YYYYMMDD
{{ prev_ds }}         # Previous execution date
{{ next_ds }}         # Next execution date
{{ execution_date }}  # Full datetime object
{{ dag }}             # DAG object
{{ task }}            # Task object
{{ params }}          # User-defined params
{{ var.value.my_var }} # Airflow variable

🔗 Next Steps:

Move to folder 2-taskflow-api/ untuk modern, cleaner approach!
"""

if __name__ == "__main__":
    print("Basic Operators examples ready!")
    print("Copy to airflow/dags/ to test.")
