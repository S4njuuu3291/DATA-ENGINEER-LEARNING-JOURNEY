# Data Serialization Contracts

## 📋 Overview

Repository ini berisi teori dan praktik tentang **Avro serialization** untuk Data Engineering, dengan fokus pada:
1. **Batch Processing** (Airflow)
2. **In-Memory Serialization** (JSON → Avro)
3. **Multi-Destination Distribution** (S3, BigQuery, PostgreSQL, dll)

---

## 📁 Struktur Folder

```
Data_Serialization_Contracts/
├── 1-teori-dasar/
│   ├── 1-teori-dasar.md                    # Filosofi Avro (basic)
│   ├── 2-avro-batch-airflow.md             # Teori Avro untuk batch processing
│   ├── 2-avro-inmemory-serialize.py        # Praktik in-memory serialization
│   ├── 3-airflow-batch-etl-example.py      # Contoh lengkap Airflow DAG
│   ├── 4-extensible-schema-registry.py     # Scalable schema management
│   ├── trade_schema.avsc                   # Schema file (Legacy)
│   ├── trade_schema_v2.avsc                # Schema file v2 (Legacy)
│   ├── trades.avro                         # Sample Avro file (Legacy)
│   ├── 1-test_avro.py                      # Test basic (Legacy)
│   └── schemas/                            # New: Extensible schema storage
│       ├── crypto_trade.json
│       ├── price_aggregate.json
│       ├── batch_metadata.json
│       ├── data_quality.json
│       └── user_activity.json
│
└── README.md (this file)

```

---

## 🎯 Learning Path

### Tahap 1: Pemahaman Fundamental
- **File:** `1-teori-dasar.md`
- **Topik:** Mengapa Avro? Masalah JSON, perbandingan binary vs textual
- **Durasi:** 30 menit

### Tahap 2: Avro untuk Batch Processing
- **File:** `2-avro-batch-airflow.md`
- **Topik:** Konteks Airflow, in-memory serialization, multi-destination pattern
- **Durasi:** 45 menit

### Tahap 3: Praktik In-Memory Serialization
- **File:** `2-avro-inmemory-serialize.py`
- **Topik:** Code examples untuk serialize JSON → Avro bytes
- **Jalankan:** `python 2-avro-inmemory-serialize.py`

### Tahap 4: Airflow ETL Pipeline
- **File:** `3-airflow-batch-etl-example.py`
- **Topik:** Contoh lengkap DAG simulation dengan multiple destinations
- **Jalankan:** `python 3-airflow-batch-etl-example.py`

### Tahap 5: Schema Management (Production-Ready)
- **File:** `4-extensible-schema-registry.py`
- **Topik:** Scalable schema registry, mudah di-extend
- **Jalankan:** `python 4-extensible-schema-registry.py`

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install fastavro
```

### 2. Run Examples
```bash
# In-memory serialization
python 2-avro-inmemory-serialize.py

# Airflow DAG simulation
python 3-airflow-batch-etl-example.py

# Schema registry
python 4-extensible-schema-registry.py
```

### 3. Output
Setiap script akan menampilkan:
- Data transformation steps
- Performance metrics (compression ratio, speed)
- Sample outputs

---

## 🏗️ Patterns & Best Practices

### Pattern 1: Serialize Once, Use Many
```python
# Extract & Serialize (once)
avro_bytes = AvroSerializer.serialize(json_data, schema)

# Use for multiple destinations
save_to_s3(avro_bytes)
save_to_bigquery(avro_bytes)
save_to_postgres(avro_bytes)
```

**Keuntungan:**
- 1 serialization, 3 destinations
- Konsisten across all targets
- CPU-efficient

### Pattern 2: Airflow XCom Communication
```python
# Task 1: Extract & Serialize
avro_bytes = serialize(data)
ti.xcom_push(key='avro_data', value=avro_bytes)

# Task 2: Validate & Process
avro_bytes = ti.xcom_pull(task_ids='task_1')
data = deserialize(avro_bytes)
validate(data)

# Task 3: Distribute
for destination in [s3, bq, pg]:
    destination.write(avro_bytes)
```

### Pattern 3: Extensible Schema Registry
```python
# Setup (once)
registry = ExtensibleSchemaRegistry("./schemas")

# Use throughout pipeline
schema = registry.get_schema("crypto_trade")
avro_bytes = serialize(data, schema)

# Easy to extend: just add new .json file to schemas/
```

---

## 📊 Performance Comparison

| Metrik | JSON | Avro | Improvement |
|--------|------|------|------------|
| **Ukuran (1M records)** | ~200 MB | ~50 MB | 75% smaller |
| **Serialize** | 2s | 0.5s | 4x faster |
| **Deserialize** | 3s | 0.3s | 10x faster |
| **Schema Validation** | Manual | Built-in | Automatic |
| **Type Safety** | Weak | Strong | Type-safe |

---

## 🔄 Avro vs JSON: Kapan Gunakan Apa?

### Gunakan Avro ✅
1. **Multi-destination pipelines** → Schema adalah kontrak
2. **Batch processing besar** → Performance & storage
3. **Data governance** → Enforce struktur sejak awal
4. **Compression needed** → Binary 75% lebih kecil
5. **Cloud native** → BigQuery, S3 native support

### Gunakan JSON ✅
1. **Prototype/debug** → Human-readable
2. **Ad-hoc queries** → Fleksibilitas
3. **Simple CSV exports** → Overhead tidak worth it
4. **API responses** → Standard for web

---

## 🛠️ Integration dengan Tools

### Airflow
```python
from airflow import DAG
from airflow.operators.python import PythonOperator

def extract_task(**context):
    data = api.get_data()
    avro_bytes = AvroSerializer.serialize(data, schema)
    context['task_instance'].xcom_push(key='avro_data', value=avro_bytes)

def transform_task(**context):
    avro_bytes = context['task_instance'].xcom_pull(task_ids='extract')
    data = AvroSerializer.deserialize(avro_bytes, schema)
    # Process...
```

### Spark
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("AvroExample").getOrCreate()

# Read Avro
df = spark.read.format("avro").load("s3://bucket/data.avro")

# Write Avro
df.write.format("avro").save("s3://bucket/output.avro")
```

### BigQuery
```python
from google.cloud import bigquery

bq_client = bigquery.Client()

# Avro data bisa langsung di-load
job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.AVRO
)
```

---

## 📚 Schema Versioning (untuk production)

Avro mendukung schema evolution:

```python
# Schema v1
v1_schema = {
    "type": "record",
    "name": "Trade",
    "fields": [
        {"name": "symbol", "type": "string"},
        {"name": "price", "type": "double"},
    ]
}

# Schema v2 (backward compatible)
v2_schema = {
    "type": "record",
    "name": "Trade",
    "fields": [
        {"name": "symbol", "type": "string"},
        {"name": "price", "type": "double"},
        {"name": "quantity", "type": "double", "default": 0},  # New field dengan default
    ]
}

# v1 data bisa dibaca dengan v2 schema (backward compatibility)
```

---

## 🔐 Data Governance Checklist

- [x] Schema defined & versioned
- [x] In-memory serialization tested
- [x] Multi-destination working
- [x] Validation before write
- [x] Error handling implemented
- [x] Performance benchmarked
- [ ] Production deployment
- [ ] Monitoring & alerts
- [ ] Disaster recovery plan

---

## 📝 Notes

### Legacy Files
- `1-test_avro.py` - Basic test (dari workshop original)
- `trade_schema.avsc` - Sample schema file
- `trades.avro` - Sample data file

Semua contoh baru focus pada **in-memory serialization** yang lebih cocok untuk Airflow.

### Next Steps
1. Integrate ke Airflow DAG
2. Test dengan real data
3. Setup monitoring
4. Document data contracts

---

## 📞 References

- **Avro Spec:** https://avro.apache.org/docs/current/
- **FastAvro:** https://github.com/fastavro/fastavro
- **Airflow XCom:** https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/xcoms.html

---

**Last Updated:** 2024-01-29  
**Author:** Data Engineering Team
