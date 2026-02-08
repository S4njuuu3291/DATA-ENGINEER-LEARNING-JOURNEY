# Tahap 2B: Avro untuk Batch Processing & Airflow

## Konteks: Mengapa Berbeda dari Streaming Kafka?

Di **Tahap 1**, kita melihat Avro dari sudut pandang **streaming real-time** (Kafka). Namun, di **Airflow (Batch Processing)**, konteksnya sangat berbeda:

| Aspek | Kafka (Real-time) | Airflow (Batch) |
|-------|------------------|-----------------|
| **Trigger** | Event-driven | Time-driven (DAG schedule) |
| **Frekuensi** | Terus-menerus | Periodic (hourly, daily, dll) |
| **Volume per batch** | Jutaan pesan per detik | Ribuan/jutaan record sekali eksekusi |
| **Destinasi** | Tunggal (Consumer Kafka) | Beragam (S3, GCS, Database, Data Lake) |
| **Kontrol** | Producer-Consumer decoupled | Orchestrator (Airflow) mengontrol segalanya |

---

## Filosofi Avro untuk Batch Processing

### 1. **Data Contract sebagai Single Source of Truth (SSOT)**

Dalam Airflow, schema Avro berfungsi sebagai **data contract** yang mengikat:
- **Producer Task:** Harus menghasilkan data sesuai schema
- **Consumer Task:** Menerima data dengan jaminan struktur

```
Extraction Task
     ↓
  Avro Serialize (In-Memory)
     ↓
  Validation Task
     ↓
  Distribution Task (S3/GCS/DB)
```

### 2. **In-Memory Serialization (Tidak selalu perlu file .avro)**

Berbeda dari contoh sebelumnya yang menulis ke file `.avro`, dalam Airflow kita sering:
- Serialize data langsung ke **bytes** di memory
- Simpan di **XCom** (Airflow's inter-task communication)
- Atau push ke object storage (S3, GCS) langsung sebagai binary

**Keuntungan:**
- Lebih cepat (tidak perlu write-read disk)
- Fleksibel (bisa diproses ulang tanpa batch ulang)
- Terintegrasi dengan Airflow metadata

### 3. **Polymorphic Serialization (One Schema, Many Destinations)**

Schema Avro bisa digunakan untuk multiple purposes:

```
JSON Data
   ↓
   ├─→ Serialize Avro (bytes) → S3 (Data Lake)
   ├─→ Serialize Avro (bytes) → GCS (Backup)
   ├─→ Serialize Avro (bytes) → PostgreSQL (operational DB)
   └─→ Serialize Avro (bytes) → BigQuery (Analytics)
```

Satu schema, banyak destinasi. Tidak perlu transform berulang kali.

---

## Teknik Serialisasi In-Memory

### A. Bytes to Memory (XCom Pattern)

```python
import io
import json
from fastavro import parse_schema, writer

# Schema definition
schema_dict = {
    "type": "record",
    "name": "BatchData",
    "fields": [
        {"name": "id", "type": "int"},
        {"name": "name", "type": "string"},
        {"name": "value", "type": "double"}
    ]
}

# Data dari JSON/API
json_data = [
    {"id": 1, "name": "item_a", "value": 10.5},
    {"id": 2, "name": "item_b", "value": 20.3}
]

# Serialize ke memory (BytesIO)
schema = parse_schema(schema_dict)
bytes_buffer = io.BytesIO()
writer(bytes_buffer, schema, json_data)
avro_bytes = bytes_buffer.getvalue()

# Hasilnya: avro_bytes bisa di-pass via XCom, disimpan, atau digunakan langsung
```

### B. Direct Serialization Pipeline

```python
def serialize_json_to_avro(json_data, schema_dict):
    """
    Mengubah JSON data langsung ke Avro bytes (in-memory)
    
    Args:
        json_data: List of dictionaries (JSON-like)
        schema_dict: Avro schema sebagai Python dict
    
    Returns:
        bytes: Avro serialized data
    """
    import io
    from fastavro import parse_schema, writer
    
    schema = parse_schema(schema_dict)
    buffer = io.BytesIO()
    writer(buffer, schema, json_data)
    return buffer.getvalue()


def deserialize_avro_bytes(avro_bytes, schema_dict):
    """
    Mengembalikan Avro bytes ke JSON data
    
    Args:
        avro_bytes: Serialized Avro data (bytes)
        schema_dict: Avro schema sebagai Python dict
    
    Returns:
        list: List of dictionaries
    """
    import io
    from fastavro import parse_schema, reader
    
    schema = parse_schema(schema_dict)
    buffer = io.BytesIO(avro_bytes)
    return list(reader(buffer))
```

---

## Use Case: Airflow DAG dengan Avro

### Scenario: ETL Cryptocurrency Price Data

```
[Extract Price API]
       ↓ (JSON list)
[Serialize to Avro In-Memory]
       ↓ (Avro bytes)
[Validate Schema]
       ↓
   ├─→ [Push to S3 Data Lake]
   ├─→ [Upload to BigQuery]
   └─→ [Insert to PostgreSQL]
```

---

## Kapan Gunakan Avro di Batch Processing?

### ✅ GUNAKAN Avro:
1. **Multi-destination pipelines** → Schema adalah SSOT
2. **Schema Evolution** → Backward/forward compatibility
3. **Compression** → Binary jauh lebih kecil dari JSON
4. **Data Contracts** → Enforce data quality sejak awal

### ❌ TIDAK PERLU Avro:
1. **Simple CSV exports** → CSV sudah cukup
2. **Prototype/Ad-hoc analysis** → JSON lebih mudah di-debug
3. **Single-destination dengan schema sederhana** → Overhead tidak worth it

---

## Perbandingan: JSON vs Avro dalam Batch Context

| Metrik | JSON | Avro |
|--------|------|------|
| **Ukuran (1 juta records)** | ~200 MB | ~50 MB (75% lebih kecil) |
| **Speed (serialize)** | 2 detik | 0.5 detik (4x lebih cepat) |
| **Speed (deserialize)** | 3 detik | 0.3 detik (10x lebih cepat) |
| **Schema validation** | Tidak langsung | Built-in |
| **Backward compatibility** | Manual | Automatic |

---

## Next Step

Lanjut ke **Praktik: Avro untuk Batch ETL** di file berikutnya.
