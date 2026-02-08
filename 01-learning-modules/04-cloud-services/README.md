# ☁️ Cloud Data Services - GCP Focus

Comprehensive guide untuk bekerja dengan **Cloud Storage, BigQuery, dan Secret Management** dalam GCP ecosystem.

## 🎯 Overview

Materi ini fokus pada 3 core services yang paling sering dipakai dalam data engineering:

1. **Cloud Storage (GCS)** - Object storage untuk raw data
2. **BigQuery** - Data warehouse untuk analytics
3. **Secret Manager** - Credential & secret management

---

## 📚 Learning Path

### 🔴 CRITICAL (Must Learn First)

#### **Folder 1: Object Storage (GCS)**
- Upload/download operations
- Blob naming conventions
- File format handling (JSON, NDJSON, CSV, Parquet)
- Batch operations
- Direct client vs abstraction layer

#### **Folder 2: Data Warehouse (BigQuery)**
- Loading data dari GCS
- Schema management (autodetect vs explicit)
- Write modes (truncate, append, merge)
- Partitioning & clustering
- Query optimization

#### **Folder 3: Secrets Management**
- Secret Manager integration
- Service account authentication
- Environment-based configuration
- Credential rotation

---

### 🟡 IMPORTANT (Production Skills)

#### **Folder 4: Integration Patterns**
- GCS → BigQuery pipelines
- Incremental loading
- Error handling & retry
- Monitoring & logging

#### **Folder 5: Testing Cloud Services**
- Mocking cloud clients
- Integration testing strategies
- Local emulators
- Test data management

---

## 📁 Folder Structure

```
Cloud_Data_Services/
├── README.md (this file)
├── 1-object-storage/
│   ├── 1-gcs-basics.md
│   ├── 2-upload-download.py
│   ├── 3-batch-operations.py
│   ├── 4-file-formats.py
│   └── README.md
├── 2-data-warehouse/
│   ├── 1-bigquery-basics.md
│   ├── 2-load-from-gcs.py
│   ├── 3-schema-management.py
│   ├── 4-partitioning-clustering.py
│   ├── 5-write-modes.py
│   └── README.md
├── 3-secrets-management/
│   ├── 1-secret-manager-basics.md
│   ├── 2-service-accounts.py
│   ├── 3-environment-config.py
│   └── README.md
├── 4-integration-patterns/
│   ├── 1-gcs-to-bigquery.py
│   ├── 2-incremental-loading.py
│   ├── 3-error-handling.py
│   └── README.md
└── 5-testing-cloud/
    ├── 1-mocking-gcs.py
    ├── 2-mocking-bigquery.py
    ├── 3-integration-tests.py
    └── README.md
```

---

## 🚀 Quick Start Examples

### 1. Upload to GCS
```python
from google.cloud import storage

def upload_to_gcs(bucket_name: str, source_file: str, destination_blob: str):
    """Upload file ke GCS."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob)
    
    blob.upload_from_filename(source_file)
    print(f"Uploaded {source_file} to gs://{bucket_name}/{destination_blob}")
```

### 2. Load to BigQuery
```python
from google.cloud import bigquery

def load_to_bigquery(
    dataset_id: str,
    table_id: str,
    source_uri: str,
    schema: list = None
):
    """Load data dari GCS ke BigQuery."""
    client = bigquery.Client()
    table_ref = f"{client.project}.{dataset_id}.{table_id}"
    
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        schema=schema,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
    )
    
    load_job = client.load_table_from_uri(
        source_uri,
        table_ref,
        job_config=job_config
    )
    
    load_job.result()  # Wait for completion
    print(f"Loaded {load_job.output_rows} rows to {table_ref}")
```

### 3. Get Secret
```python
from google.cloud import secretmanager

def get_secret(project_id: str, secret_id: str, version: str = "latest") -> str:
    """Fetch secret from Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version}"
    response = client.access_secret_version(request={"name": name})
    
    return response.payload.data.decode("UTF-8")
```

---

## 🎯 Common Patterns

### Pattern 1: File Upload with Metadata
```python
from google.cloud import storage
from datetime import datetime

def upload_with_metadata(bucket_name: str, data: bytes, filename: str):
    """Upload dengan custom metadata."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    
    # Naming convention: year/month/day/filename
    date_prefix = datetime.now().strftime("%Y/%m/%d")
    blob_name = f"{date_prefix}/{filename}"
    
    blob = bucket.blob(blob_name)
    
    # Set metadata
    blob.metadata = {
        'uploaded_by': 'etl_pipeline',
        'pipeline_version': '1.0.0',
        'source': 'api'
    }
    
    # Upload
    blob.upload_from_string(data, content_type='application/json')
    
    return f"gs://{bucket_name}/{blob_name}"
```

### Pattern 2: Incremental Load to BigQuery
```python
from google.cloud import bigquery
from datetime import datetime

def incremental_load(
    dataset_id: str,
    table_id: str,
    source_uri: str,
    partition_field: str = "created_date"
):
    """Load data dengan partitioning untuk incremental updates."""
    client = bigquery.Client()
    table_ref = f"{client.project}.{dataset_id}.{table_id}"
    
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,  # Append mode
        autodetect=True,
        time_partitioning=bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field=partition_field
        )
    )
    
    load_job = client.load_table_from_uri(source_uri, table_ref, job_config=job_config)
    load_job.result()
    
    return load_job.output_rows
```

### Pattern 3: Complete ETL Pipeline
```python
from google.cloud import storage, bigquery
import pandas as pd
from io import BytesIO

class CloudETLPipeline:
    """ETL pipeline using GCS & BigQuery."""
    
    def __init__(self, project_id: str, bucket_name: str, dataset_id: str):
        self.project_id = project_id
        self.bucket_name = bucket_name
        self.dataset_id = dataset_id
        
        self.gcs_client = storage.Client(project=project_id)
        self.bq_client = bigquery.Client(project=project_id)
    
    def extract_and_upload(self, data: pd.DataFrame, blob_name: str) -> str:
        """Extract data and upload to GCS."""
        # Convert to NDJSON
        ndjson = data.to_json(orient='records', lines=True)
        
        # Upload to GCS
        bucket = self.gcs_client.bucket(self.bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_string(ndjson, content_type='application/json')
        
        return f"gs://{self.bucket_name}/{blob_name}"
    
    def load_to_bigquery(self, source_uri: str, table_id: str):
        """Load from GCS to BigQuery."""
        table_ref = f"{self.project_id}.{self.dataset_id}.{table_id}"
        
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            autodetect=True,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
        )
        
        load_job = self.bq_client.load_table_from_uri(
            source_uri, table_ref, job_config=job_config
        )
        
        return load_job.result()
    
    def run(self, data: pd.DataFrame, table_id: str):
        """Run complete ETL."""
        # 1. Upload to GCS
        blob_name = f"staging/{table_id}/{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        source_uri = self.extract_and_upload(data, blob_name)
        
        # 2. Load to BigQuery
        job = self.load_to_bigquery(source_uri, table_id)
        
        return {
            'source_uri': source_uri,
            'rows_loaded': job.output_rows,
            'table': table_id
        }
```

---

## 🔐 Authentication Setup

### Service Account (Recommended)
```bash
# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

# In code, it's auto-detected
from google.cloud import storage
client = storage.Client()  # Uses GOOGLE_APPLICATION_CREDENTIALS
```

### With Explicit Credentials
```python
from google.cloud import storage
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file(
    '/path/to/service-account-key.json'
)

client = storage.Client(credentials=credentials, project='my-project')
```

---

## 📊 File Format Considerations

### JSON vs NDJSON (Newline-Delimited JSON)

**JSON (Array format):**
```json
[
  {"id": 1, "name": "Alice"},
  {"id": 2, "name": "Bob"}
]
```

**NDJSON (Preferred for BigQuery):**
```json
{"id": 1, "name": "Alice"}
{"id": 2, "name": "Bob"}
```

**Why NDJSON?**
- ✅ Streaming processing
- ✅ Smaller memory footprint
- ✅ Native BigQuery support
- ✅ Easy to append

### Parquet vs CSV

| Feature | Parquet | CSV |
|---------|---------|-----|
| Size | Smaller (compressed) | Larger |
| Query Speed | Fast (columnar) | Slow |
| Schema | Embedded | External/None |
| BigQuery Support | ✅ Native | ✅ Native |
| Human-Readable | ❌ | ✅ |

**Recommendation:** Use Parquet untuk large datasets, CSV untuk small/testing.

---

## 🎓 Best Practices

### ✅ DO's:

1. **Naming Conventions:**
   ```
   gs://bucket/year/month/day/dataset_name_timestamp.json
   gs://bucket/2024/01/15/users_20240115_143022.json
   ```

2. **Use Partitioning:**
   ```python
   time_partitioning=bigquery.TimePartitioning(
       type_=bigquery.TimePartitioningType.DAY,
       field="created_date"
   )
   ```

3. **Explicit Schemas:**
   ```python
   schema = [
       bigquery.SchemaField("id", "INTEGER", mode="REQUIRED"),
       bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
       bigquery.SchemaField("score", "FLOAT", mode="NULLABLE"),
   ]
   ```

4. **Error Handling:**
   ```python
   from google.api_core import exceptions
   
   try:
       load_job.result()
   except exceptions.GoogleAPIError as e:
       print(f"API Error: {e}")
   ```

### ❌ DON'Ts:

1. ❌ Commit credentials to Git
2. ❌ Use autodetect for production schemas
3. ❌ Ignore partitioning for large tables
4. ❌ Upload binary blobs as text
5. ❌ Forget to set lifecycle policies

---

## 🔗 Integration dengan Airflow

```python
from airflow.decorators import dag, task
from datetime import datetime
from google.cloud import storage, bigquery

@dag(
    dag_id='gcs_to_bigquery_pipeline',
    schedule='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False
)
def cloud_pipeline():
    
    @task
    def extract_to_gcs(bucket_name: str, blob_name: str) -> str:
        """Extract data and upload to GCS."""
        # Your extraction logic
        data = extract_from_api()
        
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_string(data)
        
        return f"gs://{bucket_name}/{blob_name}"
    
    @task
    def load_to_bq(source_uri: str, table_id: str) -> int:
        """Load from GCS to BigQuery."""
        client = bigquery.Client()
        
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            autodetect=True
        )
        
        job = client.load_table_from_uri(source_uri, table_id, job_config=job_config)
        job.result()
        
        return job.output_rows
    
    # Pipeline flow
    gcs_uri = extract_to_gcs("my-bucket", "data/{{ ds }}/output.json")
    rows = load_to_bq(gcs_uri, "my_dataset.my_table")

cloud_pipeline()
```

---

## 🧪 Testing Strategy

### Unit Tests (Mock Cloud Services)
```python
from unittest.mock import Mock, patch
import pytest

@patch('google.cloud.storage.Client')
def test_upload_to_gcs(mock_client):
    mock_bucket = Mock()
    mock_blob = Mock()
    
    mock_client.return_value.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob
    
    # Test your function
    upload_to_gcs('my-bucket', 'test.json', 'data')
    
    # Verify
    mock_blob.upload_from_string.assert_called_once()
```

### Integration Tests (Use Emulator)
```bash
# Start BigQuery emulator
docker run -p 9050:9050 ghcr.io/goccy/bigquery-emulator:latest

# Set environment
export BIGQUERY_EMULATOR_HOST=localhost:9050
```

---

## 📖 Next Steps

Setelah menguasai cloud services:
1. **Airflow Integration** - Orchestrate cloud pipelines
2. **dbt Transformation** - Transform data dalam BigQuery
3. **Monitoring** - Setup logging & alerting
4. **Cost Optimization** - Reduce cloud costs

**Master the cloud! ☁️**
