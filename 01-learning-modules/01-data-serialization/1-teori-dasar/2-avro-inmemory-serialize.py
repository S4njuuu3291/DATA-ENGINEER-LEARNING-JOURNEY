"""
Praktik: Serialisasi Avro In-Memory untuk Batch Processing (Airflow)

Fokus:
1. Serialize JSON langsung ke Avro bytes (tanpa file)
2. Kemampuan mengirim ke berbagai destinasi
3. Pattern yang cocok untuk Airflow XCom & task communication
"""

import io
import json
from typing import List, Dict, Any
from fastavro import parse_schema, writer, reader


# ============================================================================
# BAGIAN 1: Schema Definition (Reusable across tasks)
# ============================================================================

CRYPTO_TRADE_SCHEMA = {
    "type": "record",
    "name": "CryptoTrade",
    "namespace": "com.dataeng.crypto",
    "fields": [
        {"name": "symbol", "type": "string"},
        {"name": "price", "type": "double"},
        {"name": "quantity", "type": "double"},
        {"name": "event_time", "type": "long", "logicalType": "timestamp-millis"},
        {"name": "exchange", "type": "string"}
    ]
}


# ============================================================================
# BAGIAN 2: Core Serialization Functions
# ============================================================================

def serialize_json_to_avro(json_data: List[Dict[str, Any]], schema: Dict) -> bytes:
    """
    Mengubah JSON data langsung ke Avro bytes (in-memory).
    
    Cocok untuk:
    - Airflow task output (pass via XCom)
    - Temporary storage sebelum upload ke cloud
    - API response serialization
    
    Args:
        json_data: List of dictionaries (bisa dari JSON, API, database)
        schema: Avro schema definition (dict)
    
    Returns:
        bytes: Serialized Avro data (binary format)
    """
    schema_parsed = parse_schema(schema)
    buffer = io.BytesIO()
    writer(buffer, schema_parsed, json_data)
    return buffer.getvalue()


def deserialize_avro_bytes(avro_bytes: bytes, schema: Dict) -> List[Dict[str, Any]]:
    """
    Mengubah Avro bytes kembali ke JSON data.
    
    Cocok untuk:
    - Membaca data dari XCom Airflow
    - Validasi sebelum commit ke database
    - Debugging/inspection
    
    Args:
        avro_bytes: Serialized Avro data (binary)
        schema: Avro schema definition (dict)
    
    Returns:
        list: List of dictionaries (JSON-like)
    """
    schema_parsed = parse_schema(schema)
    buffer = io.BytesIO(avro_bytes)
    return list(reader(buffer))


# ============================================================================
# BAGIAN 3: Practical Example - Extract & Serialize
# ============================================================================

def example_1_basic_serialize():
    """
    Contoh 1: Serialize data dari JSON API response langsung ke Avro
    (Simulasi: data dari Binance API)
    """
    print("=" * 60)
    print("CONTOH 1: Basic In-Memory Serialization")
    print("=" * 60)
    
    # Simulasi: Data dari Binance API (JSON)
    api_response = [
        {
            "symbol": "BTCUSDT",
            "price": 45000.50,
            "quantity": 0.5,
            "event_time": 1700000000000,
            "exchange": "BINANCE"
        },
        {
            "symbol": "ETHUSDT",
            "price": 3200.75,
            "quantity": 10.0,
            "event_time": 1700000001000,
            "exchange": "BINANCE"
        },
        {
            "symbol": "BNBUSDT",
            "price": 420.30,
            "quantity": 5.0,
            "event_time": 1700000002000,
            "exchange": "BINANCE"
        }
    ]
    
    print(f"\n1️⃣  Input (JSON data dari API):")
    print(f"   Tipe: {type(api_response)}")
    print(f"   Jumlah records: {len(api_response)}")
    print(f"   Ukuran JSON string: {len(json.dumps(api_response))} bytes")
    
    # Serialize ke Avro
    avro_bytes = serialize_json_to_avro(api_response, CRYPTO_TRADE_SCHEMA)
    
    print(f"\n2️⃣  Output (Avro bytes):")
    print(f"   Tipe: {type(avro_bytes)}")
    print(f"   Ukuran Avro: {len(avro_bytes)} bytes")
    print(f"   Efisiensi: {((len(json.dumps(api_response)) - len(avro_bytes)) / len(json.dumps(api_response)) * 100):.1f}% lebih kecil")
    
    # Deserialize kembali untuk verifikasi
    recovered_data = deserialize_avro_bytes(avro_bytes, CRYPTO_TRADE_SCHEMA)
    print(f"\n3️⃣  Verifikasi (Deserialize kembali):")
    print(f"   Data utuh: {recovered_data == api_response}")
    print(f"   Contoh record pertama: {recovered_data[0]}")
    
    return avro_bytes


# ============================================================================
# BAGIAN 4: Multi-Destination Pattern
# ============================================================================

def save_to_file(avro_bytes: bytes, filepath: str) -> None:
    """Simpan Avro bytes ke file (.avro)"""
    with open(filepath, "wb") as f:
        f.write(avro_bytes)
    print(f"✅ Tersimpan ke file: {filepath}")


def simulate_s3_upload(avro_bytes: bytes, bucket: str, key: str) -> None:
    """Simulasi upload ke S3 (dalam praktik: gunakan boto3)"""
    size_mb = len(avro_bytes) / 1024 / 1024
    print(f"✅ Upload simulasi ke S3: s3://{bucket}/{key} ({size_mb:.2f} MB)")
    # Dalam praktik real:
    # s3_client.put_object(Bucket=bucket, Key=key, Body=avro_bytes)


def simulate_bigquery_insert(avro_bytes: bytes, project: str, dataset: str, table: str, schema: Dict) -> None:
    """Simulasi insert ke BigQuery (dalam praktik: gunakan google-cloud-bigquery)"""
    data = deserialize_avro_bytes(avro_bytes, schema)
    print(f"✅ Insert simulasi ke BigQuery: {project}.{dataset}.{table}")
    print(f"   Rows: {len(data)}")
    # Dalam praktik real:
    # bq_client.insert_rows_json(table_ref, data)


def simulate_postgres_insert(avro_bytes: bytes, conn_string: str, table: str, schema: Dict) -> None:
    """Simulasi insert ke PostgreSQL (dalam praktik: gunakan psycopg2)"""
    data = deserialize_avro_bytes(avro_bytes, schema)
    print(f"✅ Insert simulasi ke PostgreSQL: {conn_string}")
    print(f"   Table: {table}")
    print(f"   Rows: {len(data)}")
    # Dalam praktik real:
    # conn = psycopg2.connect(conn_string)
    # for row in data:
    #     cursor.execute(f"INSERT INTO {table} VALUES ...")


def example_2_multi_destination():
    """
    Contoh 2: Satu Avro serialization, multiple destinations
    (Pattern: Extract once, distribute everywhere)
    """
    print("\n" + "=" * 60)
    print("CONTOH 2: Multi-Destination Distribution")
    print("=" * 60)
    
    # Step 1: Extract & Serialize sekali
    json_data = [
        {"symbol": "BTCUSDT", "price": 45000.0, "quantity": 1.0, 
         "event_time": 1700000000000, "exchange": "BINANCE"},
        {"symbol": "ETHUSDT", "price": 3200.0, "quantity": 5.0, 
         "event_time": 1700000001000, "exchange": "BINANCE"},
    ]
    
    avro_bytes = serialize_json_to_avro(json_data, CRYPTO_TRADE_SCHEMA)
    
    print(f"\n📦 Serialized data size: {len(avro_bytes)} bytes")
    print("\n🚀 Distribusi ke berbagai destinasi:\n")
    
    # Step 2: Kirim ke berbagai tempat
    simulate_s3_upload(avro_bytes, "my-data-lake", "crypto/2024/01/trades.avro")
    simulate_bigquery_insert(avro_bytes, "my-project", "raw", "crypto_trades", CRYPTO_TRADE_SCHEMA)
    simulate_postgres_insert(avro_bytes, "postgresql://user:pass@localhost/db", "crypto_trades", CRYPTO_TRADE_SCHEMA)
    
    print("\n✨ Keuntungan:")
    print("   • Extract hanya 1 kali")
    print("   • Semua destinasi dapat data dengan struktur identik")
    print("   • Data validated sekali, berlaku untuk semua")


# ============================================================================
# BAGIAN 5: Airflow XCom Pattern
# ============================================================================

def example_3_airflow_xccom_pattern():
    """
    Contoh 3: Pattern Airflow XCom untuk inter-task communication
    
    Alur:
    Task 1: Extract data dari API → Serialize Avro → push ke XCom
    Task 2: Pull dari XCom → Deserialize → Validate → push hasil
    Task 3: Pull dari XCom → Distribute ke destination
    """
    print("\n" + "=" * 60)
    print("CONTOH 3: Airflow XCom Pattern")
    print("=" * 60)
    
    print("\n📋 Simulasi Airflow DAG:\n")
    
    # ============ TASK 1: Extract & Serialize ============
    print("Task 1: extract_and_serialize")
    print("-" * 40)
    
    # Simulasi: API call
    extracted_data = [
        {"symbol": "BTCUSDT", "price": 45000.0, "quantity": 1.0,
         "event_time": 1700000000000, "exchange": "BINANCE"},
        {"symbol": "ETHUSDT", "price": 3200.0, "quantity": 5.0,
         "event_time": 1700000001000, "exchange": "BINANCE"},
    ]
    
    avro_bytes = serialize_json_to_avro(extracted_data, CRYPTO_TRADE_SCHEMA)
    
    print(f"✅ Data extracted: {len(extracted_data)} records")
    print(f"✅ Serialized to Avro: {len(avro_bytes)} bytes")
    print(f"✅ Push ke XCom: task_instance.xcom_push(key='avro_data', value={repr(avro_bytes[:20])}...)")
    
    # ============ TASK 2: Validate ============
    print("\nTask 2: validate_data")
    print("-" * 40)
    
    # Simulasi: Pull dari XCom
    received_bytes = avro_bytes  # Dalam Airflow: ti.xcom_pull(task_ids='task_1', key='avro_data')
    
    # Deserialize untuk validasi
    deserialized = deserialize_avro_bytes(received_bytes, CRYPTO_TRADE_SCHEMA)
    
    validation_passed = all("symbol" in r and "price" in r for r in deserialized)
    print(f"✅ Pull dari XCom: {len(received_bytes)} bytes")
    print(f"✅ Deserialized: {len(deserialized)} records")
    print(f"✅ Validation: {'PASSED' if validation_passed else 'FAILED'}")
    print(f"✅ Push validated data back ke XCom")
    
    # ============ TASK 3: Distribute ============
    print("\nTask 3: distribute_data")
    print("-" * 40)
    
    # Simulasi: Pull dan distribute
    data_to_distribute = received_bytes
    
    print(f"✅ Pull dari XCom: {len(data_to_distribute)} bytes")
    print(f"✅ Send ke S3 Data Lake")
    print(f"✅ Send ke BigQuery")
    print(f"✅ Send ke PostgreSQL")
    
    return avro_bytes


# ============================================================================
# BAGIAN 6: Real-world comparison
# ============================================================================

def example_4_compression_comparison():
    """
    Contoh 4: Perbandingan ukuran JSON vs Avro dengan data besar
    """
    print("\n" + "=" * 60)
    print("CONTOH 4: Compression & Performance Comparison")
    print("=" * 60)
    
    # Generate sample data (100 records)
    import random
    from datetime import datetime, timedelta
    
    base_time = int(datetime.now().timestamp() * 1000)
    
    large_dataset = [
        {
            "symbol": random.choice(["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "DOGEUSDT"]),
            "price": round(random.uniform(100, 50000), 2),
            "quantity": round(random.uniform(0.001, 100), 3),
            "event_time": base_time + i * 1000,
            "exchange": "BINANCE"
        }
        for i in range(100)
    ]
    
    # Format JSON
    json_str = json.dumps(large_dataset)
    json_bytes = json_str.encode('utf-8')
    
    # Format Avro
    avro_bytes = serialize_json_to_avro(large_dataset, CRYPTO_TRADE_SCHEMA)
    
    print(f"\n📊 Dataset: {len(large_dataset)} records\n")
    print(f"{'Format':<15} {'Size':<15} {'Compression':<15}")
    print("-" * 45)
    print(f"{'JSON':<15} {len(json_bytes):<15} bytes  (baseline)")
    print(f"{'Avro':<15} {len(avro_bytes):<15} bytes  ({((1 - len(avro_bytes) / len(json_bytes)) * 100):.1f}% smaller)")
    
    return avro_bytes, json_bytes


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print("\n" + "🚀" * 30)
    print("AVRO IN-MEMORY SERIALIZATION FOR BATCH PROCESSING (AIRFLOW)")
    print("🚀" * 30)
    
    # Run examples
    avro_bytes_1 = example_1_basic_serialize()
    example_2_multi_destination()
    example_3_airflow_xccom_pattern()
    avro_bytes_4, json_bytes_4 = example_4_compression_comparison()
    
    print("\n" + "=" * 60)
    print("KESIMPULAN")
    print("=" * 60)
    print("""
✨ Key Takeaways:

1. **In-Memory Serialization**
   - Tidak perlu file .avro di disk
   - Langsung dari JSON ke Avro bytes
   - Cocok untuk Airflow XCom (lightweight communication)

2. **Multi-Destination**
   - Serialize sekali, kirim kemana saja
   - S3, BigQuery, PostgreSQL, semua support Avro bytes
   - SSOT (Single Source of Truth) untuk schema

3. **Airflow Pattern**
   Task 1: Extract JSON → Serialize Avro → XCom
   Task 2: Pull Avro → Validate → XCom
   Task 3: Pull Avro → Distribute ke destination

4. **Performance**
   - 50-75% lebih kecil dibanding JSON
   - 4x lebih cepat serialize
   - 10x lebih cepat deserialize

5. **Data Governance**
   - Schema sebagai kontrak (enforced)
   - Backward/forward compatibility
   - Type safety dari awal
    """)
