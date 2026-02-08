# 🏗️ Data Pipeline Architecture

Comprehensive guide untuk design & implement **production-ready data pipelines**.

## 🎯 What is Data Pipeline Architecture?

**Architecture** = Blueprint untuk build reliable, scalable data pipelines.

**Key Questions:**
- How to structure ETL/ELT workflows?
- Where should transformations happen?
- How to handle failures?
- How to monitor & debug?

---

## 📚 Core Patterns

### 🔴 CRITICAL: ETL vs ELT

#### **ETL (Extract-Transform-Load)**
```
API → Python/Spark → Transform → Load → Data Warehouse
```

**Use when:**
- ✅ Data needs heavy processing before loading
- ✅ Source data is messy
- ✅ Need to mask/encrypt sensitive data
- ✅ Complex business logic

**Tools:** Python, Spark, Pandas

---

#### **ELT (Extract-Load-Transform)**
```
API → Load → Data Warehouse → Transform (dbt/SQL)
```

**Use when:**
- ✅ Warehouse has powerful compute (BigQuery, Snowflake)
- ✅ Want audit trail of raw data
- ✅ Need different views of same data
- ✅ SQL-first team

**Tools:** Fivetran, Airbyte, dbt

---

## 📁 Folder Structure

```
Data_Pipeline_Architecture/
├── README.md (this file)
├── 1-etl-elt-patterns/
│   ├── 1-when-to-use-etl.md
│   ├── 2-when-to-use-elt.md
│   ├── 3-hybrid-approach.py
│   └── README.md
├── 2-data-modeling/
│   ├── 1-dimensional-modeling.md
│   ├── 2-fact-dimension-tables.md
│   ├── 3-scd-patterns.md
│   ├── 4-denormalization.md
│   └── README.md
├── 3-data-quality/
│   ├── 1-schema-validation.py
│   ├── 2-type-conversion.py
│   ├── 3-deduplication.py
│   ├── 4-freshness-checks.py
│   └── README.md
├── 4-file-formats/
│   ├── 1-json-vs-ndjson.md
│   ├── 2-csv-best-practices.md
│   ├── 3-parquet-columnar.md
│   ├── 4-format-selection.md
│   └── README.md
└── 5-orchestration-patterns/
    ├── 1-task-dependencies.md
    ├── 2-idempotency.md
    ├── 3-backfilling.md
    └── README.md
```

---

## 🎨 Design Patterns

### Pattern 1: Medallion Architecture (Bronze/Silver/Gold)

```
Bronze (Raw)     → Silver (Cleaned)  → Gold (Aggregated)
Landing Zone       Validated Data      Business Metrics
```

**Implementation:**
```
gs://bucket/bronze/2024/01/15/raw_data.json
   ↓
gs://bucket/silver/2024/01/15/cleaned_data.parquet
   ↓
bq://project.gold.daily_metrics
```

---

### Pattern 2: Lambda Architecture

```
Batch Layer:    Historical data processing (Spark, dbt)
         ↓
Speed Layer:    Real-time streaming (Kafka, Spark Streaming)
         ↓
Serving Layer:  Combined view untuk queries
```

---

### Pattern 3: Data Vault 2.0

**For:**
- Large enterprises
- Regulatory compliance
- Full audit trail

**Structure:**
- Hubs (business keys)
- Links (relationships)
- Satellites (descriptive data)

---

## 🚀 Complete Pipeline Example

```python
from airflow.decorators import dag, task
from google.cloud import storage, bigquery
import pandas as pd
from datetime import datetime

@dag(
    dag_id='complete_data_pipeline',
    schedule='@daily',
    start_date=datetime(2024, 1, 1)
)
def data_pipeline():
    
    # EXTRACT
    @task
    def extract_from_api() -> str:
        """Extract data dari API."""
        import requests
        
        response = requests.get('https://api.example.com/data')
        data = response.json()
        
        # Save to GCS (Bronze layer)
        client = storage.Client()
        bucket = client.bucket('my-bucket')
        
        blob_name = f"bronze/{datetime.now().strftime('%Y/%m/%d')}/raw_data.json"
        blob = bucket.blob(blob_name)
        blob.upload_from_string(json.dumps(data))
        
        return f"gs://my-bucket/{blob_name}"
    
    # TRANSFORM
    @task
    def transform_data(bronze_uri: str) -> str:
        """Transform & validate data."""
        # Read from bronze
        df = pd.read_json(bronze_uri.replace('gs://', '/tmp/'))
        
        # Clean & validate
        df = df.dropna(subset=['id', 'created_date'])
        df['created_date'] = pd.to_datetime(df['created_date'])
        df = df[df['score'] >= 0]  # Remove invalid scores
        
        # Save to GCS (Silver layer)
        silver_path = bronze_uri.replace('bronze', 'silver').replace('.json', '.parquet')
        df.to_parquet(silver_path.replace('gs://', '/tmp/'))
        
        # Upload to GCS
        client = storage.Client()
        # ... upload logic
        
        return silver_path
    
    # LOAD
    @task
    def load_to_bigquery(silver_uri: str):
        """Load to BigQuery."""
        client = bigquery.Client()
        
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.PARQUET,
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            time_partitioning=bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY,
                field='created_date'
            )
        )
        
        load_job = client.load_table_from_uri(
            silver_uri,
            'project.dataset.table',
            job_config=job_config
        )
        
        load_job.result()
        return load_job.output_rows
    
    # TRANSFORM in Warehouse (Gold layer)
    @task
    def transform_in_warehouse():
        """Run dbt untuk create gold tables."""
        import subprocess
        subprocess.run(['dbt', 'run', '--select', 'marts.*'])
    
    # VALIDATE
    @task
    def validate_data_quality():
        """Run data quality checks."""
        client = bigquery.Client()
        
        # Check freshness
        query = """
        SELECT MAX(created_date) as max_date
        FROM `project.dataset.table`
        """
        result = client.query(query).to_dataframe()
        
        max_date = result['max_date'].iloc[0]
        if (datetime.now().date() - max_date).days > 1:
            raise ValueError("Data is stale!")
    
    # Pipeline flow
    bronze_uri = extract_from_api()
    silver_uri = transform_data(bronze_uri)
    rows_loaded = load_to_bigquery(silver_uri)
    transform_in_warehouse()
    validate_data_quality()

data_pipeline()
```

---

## 📊 Data Modeling Concepts

### Fact Tables (Measurements)
```sql
-- Fact: Order transactions
CREATE TABLE fct_orders (
    order_id INT64,
    user_id INT64,
    product_id INT64,
    order_date DATE,
    quantity INT64,
    amount FLOAT64,
    
    -- Foreign keys to dimensions
    FOREIGN KEY (user_id) REFERENCES dim_users(user_id),
    FOREIGN KEY (product_id) REFERENCES dim_products(product_id)
)
PARTITION BY order_date;
```

### Dimension Tables (Context)
```sql
-- Dimension: Users
CREATE TABLE dim_users (
    user_id INT64 PRIMARY KEY,
    user_name STRING,
    email STRING,
    country STRING,
    created_date DATE,
    user_status STRING
);
```

---

## 🎯 Best Practices

### ✅ Idempotency (Critical!)
```python
# ❌ Not idempotent
def load_data():
    df = extract_data()
    df.to_sql('table', engine, if_exists='append')  # Duplicates on retry!

# ✅ Idempotent
def load_data(execution_date):
    df = extract_data()
    
    # Delete existing data for this date
    engine.execute(f"DELETE FROM table WHERE date = '{execution_date}'")
    
    # Then insert
    df.to_sql('table', engine, if_exists='append')
```

---

### ✅ Partitioning for Performance
```sql
-- BigQuery partitioning
CREATE TABLE dataset.table (
    id INT64,
    value FLOAT64,
    created_date DATE
)
PARTITION BY created_date
CLUSTER BY id;

-- Query optimization
SELECT *
FROM dataset.table
WHERE created_date = '2024-01-15'  -- Only scans 1 partition!
```

---

### ✅ Data Quality Checks
```python
def validate_schema(df: pd.DataFrame):
    """Validate DataFrame schema."""
    required_columns = ['id', 'name', 'created_date']
    
    for col in required_columns:
        assert col in df.columns, f"Missing column: {col}"
    
    # Type checks
    assert df['id'].dtype == 'int64'
    assert pd.api.types.is_datetime64_any_dtype(df['created_date'])
    
    # Null checks
    assert df['id'].isnull().sum() == 0
    
    # Value checks
    assert (df['score'] >= 0).all()
    assert (df['score'] <= 100).all()
```

---

## 🔗 Pipeline Patterns Comparison

| Pattern | Use Case | Complexity | Cost |
|---------|----------|------------|------|
| **ETL** | Heavy transformation | Medium | Medium |
| **ELT** | SQL transformations | Low | Low (warehouse compute) |
| **Streaming** | Real-time data | High | High |
| **Batch** | Periodic loads | Low | Low |
| **Hybrid** | Best of both | High | Variable |

---

## 📖 Further Reading

- Dimensional Modeling: Kimball's "The Data Warehouse Toolkit"
- Pipeline Patterns: "Designing Data-Intensive Applications"
- Best Practices: "The Data Engineering Cookbook"

**Build bulletproof pipelines! 🏗️**
