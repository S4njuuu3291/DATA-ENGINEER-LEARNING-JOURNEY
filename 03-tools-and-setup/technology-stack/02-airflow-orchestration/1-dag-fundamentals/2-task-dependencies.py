"""
TASK DEPENDENCIES - Berbagai Cara Set Dependencies

Topics:
- Linear dependencies
- Parallel dependencies  
- Complex dependencies
- Cross dependencies

Cara run (simulation, tidak perlu Airflow):
    python 2-task-dependencies.py
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# ==========================================
# TASK FUNCTIONS
# ==========================================

def extract_api_1():
    print("📥 Extracting from API 1...")
    return "api1_data"

def extract_api_2():
    print("📥 Extracting from API 2...")
    return "api2_data"

def extract_api_3():
    print("📥 Extracting from API 3...")
    return "api3_data"

def transform_data():
    print("🔄 Transforming data...")
    return "transformed_data"

def validate_data():
    print("✅ Validating data...")
    return "validated_data"

def load_to_staging():
    print("📤 Loading to staging...")
    return "staging_loaded"

def load_to_production():
    print("📤 Loading to production...")
    return "production_loaded"

def send_notification():
    print("📧 Sending notification...")
    return "notification_sent"

def cleanup_temp_files():
    print("🧹 Cleaning up...")
    return "cleaned"

# ==========================================
# PATTERN 1: LINEAR DEPENDENCIES
# ==========================================

def create_linear_dag():
    """
    Simple linear flow: A → B → C → D
    
    Use case: Sequential ETL
    """
    default_args = {
        'owner': 'data_engineer',
        'retries': 1,
        'retry_delay': timedelta(minutes=5)
    }
    
    with DAG(
        dag_id='pattern_1_linear',
        default_args=default_args,
        schedule='@daily',
        start_date=datetime(2024, 1, 1),
        catchup=False,
        tags=['example', 'linear']
    ) as dag:
        
        extract = PythonOperator(
            task_id='extract',
            python_callable=extract_api_1
        )
        
        transform = PythonOperator(
            task_id='transform',
            python_callable=transform_data
        )
        
        validate = PythonOperator(
            task_id='validate',
            python_callable=validate_data
        )
        
        load = PythonOperator(
            task_id='load',
            python_callable=load_to_production
        )
        
        # Linear dependency
        extract >> transform >> validate >> load
        
    return dag

# ==========================================
# PATTERN 2: PARALLEL THEN MERGE
# ==========================================

def create_parallel_merge_dag():
    """
    Parallel extraction, then merge:
    
        A1 ─┐
        A2 ─┤→ B → C
        A3 ─┘
    
    Use case: Multiple data sources yang bisa diambil parallel
    """
    default_args = {
        'owner': 'data_engineer',
        'retries': 2,
        'retry_delay': timedelta(minutes=5)
    }
    
    with DAG(
        dag_id='pattern_2_parallel_merge',
        default_args=default_args,
        schedule='@daily',
        start_date=datetime(2024, 1, 1),
        catchup=False,
        tags=['example', 'parallel']
    ) as dag:
        
        # Parallel extraction tasks
        extract1 = PythonOperator(
            task_id='extract_api_1',
            python_callable=extract_api_1
        )
        
        extract2 = PythonOperator(
            task_id='extract_api_2',
            python_callable=extract_api_2
        )
        
        extract3 = PythonOperator(
            task_id='extract_api_3',
            python_callable=extract_api_3
        )
        
        # Merge task (waits for all extractions)
        transform = PythonOperator(
            task_id='transform_all',
            python_callable=transform_data
        )
        
        # Load task
        load = PythonOperator(
            task_id='load',
            python_callable=load_to_production
        )
        
        # Dependencies: All extracts → transform → load
        [extract1, extract2, extract3] >> transform >> load
        
    return dag

# ==========================================
# PATTERN 3: SPLIT THEN PARALLEL
# ==========================================

def create_split_parallel_dag():
    """
    One source, multiple destinations:
    
             ┌→ B1
        A → ─┼→ B2
             └→ B3
    
    Use case: One extraction, load ke multiple destinations
    """
    default_args = {
        'owner': 'data_engineer',
        'retries': 1,
        'retry_delay': timedelta(minutes=5)
    }
    
    with DAG(
        dag_id='pattern_3_split_parallel',
        default_args=default_args,
        schedule='@daily',
        start_date=datetime(2024, 1, 1),
        catchup=False,
        tags=['example', 'split']
    ) as dag:
        
        # Single extraction
        extract = PythonOperator(
            task_id='extract',
            python_callable=extract_api_1
        )
        
        # Multiple parallel loads
        load_staging = PythonOperator(
            task_id='load_staging',
            python_callable=load_to_staging
        )
        
        load_production = PythonOperator(
            task_id='load_production',
            python_callable=load_to_production
        )
        
        notify = PythonOperator(
            task_id='notify',
            python_callable=send_notification
        )
        
        # Dependencies: extract → [multiple tasks in parallel]
        extract >> [load_staging, load_production, notify]
        
    return dag

# ==========================================
# PATTERN 4: COMPLEX DIAMOND PATTERN
# ==========================================

def create_diamond_dag():
    """
    Diamond pattern:
    
            A
           ╱ ╲
          B   C
           ╲ ╱
            D
    
    Use case: Parallel processing then merge
    """
    default_args = {
        'owner': 'data_engineer',
        'retries': 2,
        'retry_delay': timedelta(minutes=5)
    }
    
    with DAG(
        dag_id='pattern_4_diamond',
        default_args=default_args,
        schedule='@daily',
        start_date=datetime(2024, 1, 1),
        catchup=False,
        tags=['example', 'diamond']
    ) as dag:
        
        extract = PythonOperator(
            task_id='extract',
            python_callable=extract_api_1
        )
        
        # Parallel branches
        transform_branch1 = PythonOperator(
            task_id='transform_branch1',
            python_callable=transform_data
        )
        
        transform_branch2 = PythonOperator(
            task_id='transform_branch2',
            python_callable=validate_data
        )
        
        # Merge point
        load = PythonOperator(
            task_id='load',
            python_callable=load_to_production
        )
        
        # Diamond dependencies
        extract >> [transform_branch1, transform_branch2] >> load
        
    return dag

# ==========================================
# PATTERN 5: FULL PIPELINE WITH CLEANUP
# ==========================================

def create_full_pipeline_dag():
    """
    Production-like pipeline:
    
        E1 ─┐
        E2 ─┤→ T → V → L → N
        E3 ─┘              ↓
                           C (cleanup)
    
    Use case: Real ETL dengan validation, notification & cleanup
    """
    default_args = {
        'owner': 'data_engineer',
        'email': ['data-team@company.com'],
        'email_on_failure': True,
        'retries': 3,
        'retry_delay': timedelta(minutes=5),
        'retry_exponential_backoff': True
    }
    
    with DAG(
        dag_id='pattern_5_full_pipeline',
        default_args=default_args,
        description='Production ETL pipeline dengan cleanup',
        schedule='0 2 * * *',  # 2 AM daily
        start_date=datetime(2024, 1, 1),
        catchup=False,
        tags=['production', 'etl']
    ) as dag:
        
        # Parallel extractions
        extract1 = PythonOperator(task_id='extract_api_1', python_callable=extract_api_1)
        extract2 = PythonOperator(task_id='extract_api_2', python_callable=extract_api_2)
        extract3 = PythonOperator(task_id='extract_api_3', python_callable=extract_api_3)
        
        # Sequential processing
        transform = PythonOperator(task_id='transform', python_callable=transform_data)
        validate = PythonOperator(task_id='validate', python_callable=validate_data)
        load = PythonOperator(task_id='load', python_callable=load_to_production)
        notify = PythonOperator(task_id='notify', python_callable=send_notification)
        cleanup = PythonOperator(task_id='cleanup', python_callable=cleanup_temp_files)
        
        # Complex dependencies
        [extract1, extract2, extract3] >> transform >> validate >> load >> notify
        notify >> cleanup  # Cleanup after notification
        
    return dag

# ==========================================
# PATTERN 6: CROSS DEPENDENCIES
# ==========================================

def create_cross_dependencies_dag():
    """
    Cross dependencies (advanced):
    
        A ──→ B ──→ D
        │     ↗     ↑
        └──→ C ─────┘
    
    Use case: Complex workflows dengan multiple paths
    """
    default_args = {
        'owner': 'data_engineer',
        'retries': 1,
        'retry_delay': timedelta(minutes=5)
    }
    
    with DAG(
        dag_id='pattern_6_cross_dependencies',
        default_args=default_args,
        schedule='@daily',
        start_date=datetime(2024, 1, 1),
        catchup=False,
        tags=['example', 'advanced']
    ) as dag:
        
        taskA = PythonOperator(task_id='taskA', python_callable=extract_api_1)
        taskB = PythonOperator(task_id='taskB', python_callable=transform_data)
        taskC = PythonOperator(task_id='taskC', python_callable=validate_data)
        taskD = PythonOperator(task_id='taskD', python_callable=load_to_production)
        
        # Cross dependencies
        taskA >> taskB >> taskD
        taskA >> taskC >> taskB  # C also feeds into B
        taskC >> taskD  # C also feeds into D
        
    return dag

# ==========================================
# ALTERNATIVE SYNTAX
# ==========================================

def demo_alternative_syntax():
    """
    Different ways to set dependencies.
    All achieve the same result!
    """
    with DAG(
        dag_id='alternative_syntax_demo',
        schedule='@daily',
        start_date=datetime(2024, 1, 1),
        catchup=False
    ) as dag:
        
        task1 = PythonOperator(task_id='task1', python_callable=extract_api_1)
        task2 = PythonOperator(task_id='task2', python_callable=transform_data)
        task3 = PythonOperator(task_id='task3', python_callable=load_to_production)
        
        # Method 1: Bitshift (most common)
        task1 >> task2 >> task3
        
        # Method 2: set_downstream
        # task1.set_downstream(task2)
        # task2.set_downstream(task3)
        
        # Method 3: set_upstream
        # task3.set_upstream(task2)
        # task2.set_upstream(task1)
        
        # Method 4: List notation
        # task1 >> [task2] >> [task3]
        
        # Method 5: Mixed
        # task1.set_downstream([task2])
        # task2 >> task3

# ==========================================
# BEST PRACTICES
# ==========================================

"""
✅ DO's:
1. Use >> operator (most readable)
2. Group parallel tasks in lists: [task1, task2] >> task3
3. Add comments untuk complex dependencies
4. Name tasks descriptively
5. Keep dependencies simple when possible

❌ DON'Ts:
1. Don't create circular dependencies (A >> B >> A)
2. Don't make dependencies too complex (hard to debug)
3. Don't use all methods mixed (stick to one style)
4. Don't create unnecessary task splits

TIPS:
- Visualize DAG di Airflow UI untuk cek dependencies
- Test dengan small sample data dulu
- Use tags untuk group related DAGs
- Monitor task duration untuk optimize parallelization
"""

# ==========================================
# MAIN (untuk testing)
# ==========================================

if __name__ == "__main__":
    print("=" * 60)
    print("TASK DEPENDENCIES PATTERNS")
    print("=" * 60)
    print("\n📚 Patterns covered:")
    print("1. Linear: A → B → C → D")
    print("2. Parallel merge: [A1, A2, A3] → B → C")
    print("3. Split parallel: A → [B1, B2, B3]")
    print("4. Diamond: A → [B, C] → D")
    print("5. Full pipeline dengan cleanup")
    print("6. Cross dependencies (advanced)")
    print("\n✅ Run these DAGs in Airflow to see them in action!")
    print("\nCopy file ini ke airflow/dags/ folder.")
