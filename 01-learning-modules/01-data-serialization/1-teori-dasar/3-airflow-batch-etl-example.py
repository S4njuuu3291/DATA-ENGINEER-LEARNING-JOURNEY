"""
Practical ETL Pipeline untuk Airflow: Avro-based Batch Processing

Ini adalah contoh lengkap bagaimana menggunakan Avro dalam Airflow DAG
untuk batch processing dengan multiple destinations.

Use Case:
- Extract cryptocurrency price dari API
- Serialize ke Avro
- Validate schema
- Distribute ke: S3 (Data Lake), PostgreSQL (Operational DB), BigQuery (Analytics)
"""

import io
import json
from datetime import datetime
from typing import List, Dict, Any
from fastavro import parse_schema, writer, reader


# ============================================================================
# PART 1: Schema Registry (Reusable across DAG)
# ============================================================================

class AvroSchemaRegistry:
    """
    Centralized schema management untuk semua Avro schemas
    (Dalam praktik real: gunakan Confluent Schema Registry)
    """
    
    schemas = {
        "crypto_trade": {
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
        },
        "price_aggregate": {
            "type": "record",
            "name": "PriceAggregate",
            "namespace": "com.dataeng.crypto",
            "fields": [
                {"name": "symbol", "type": "string"},
                {"name": "avg_price", "type": "double"},
                {"name": "min_price", "type": "double"},
                {"name": "max_price", "type": "double"},
                {"name": "total_quantity", "type": "double"},
                {"name": "record_count", "type": "int"},
                {"name": "batch_date", "type": "string"}
            ]
        }
    }
    
    @classmethod
    def get_schema(cls, schema_name: str) -> Dict:
        if schema_name not in cls.schemas:
            raise ValueError(f"Schema '{schema_name}' not found")
        return cls.schemas[schema_name]


# ============================================================================
# PART 2: Serialization Utilities
# ============================================================================

class AvroSerializer:
    """Utility untuk serialize/deserialize Avro data"""
    
    @staticmethod
    def serialize(data: List[Dict[str, Any]], schema_name: str) -> bytes:
        """Serialize JSON data ke Avro bytes"""
        schema_dict = AvroSchemaRegistry.get_schema(schema_name)
        schema = parse_schema(schema_dict)
        
        buffer = io.BytesIO()
        writer(buffer, schema, data)
        
        return buffer.getvalue()
    
    @staticmethod
    def deserialize(avro_bytes: bytes, schema_name: str) -> List[Dict[str, Any]]:
        """Deserialize Avro bytes ke JSON data"""
        schema_dict = AvroSchemaRegistry.get_schema(schema_name)
        schema = parse_schema(schema_dict)
        
        buffer = io.BytesIO(avro_bytes)
        return list(reader(buffer))
    
    @staticmethod
    def get_size_info(avro_bytes: bytes, json_str: str = None) -> Dict[str, Any]:
        """Get compression info"""
        avro_size = len(avro_bytes)
        json_size = len(json_str) if json_str else 0
        
        return {
            "avro_size_bytes": avro_size,
            "json_size_bytes": json_size,
            "compression_ratio": ((1 - avro_size / json_size) * 100) if json_size > 0 else 0,
            "avro_size_mb": avro_size / 1024 / 1024
        }


# ============================================================================
# PART 3: Airflow Task Functions (DAG Components)
# ============================================================================

class AirflowTasks:
    """
    Simulasi Airflow Task Functions
    (Dalam praktik: import dari airflow.operators.python)
    """
    
    @staticmethod
    def task_extract_from_api(**context):
        """
        Task 1: Extract data dari API (simulasi)
        Output: JSON data
        """
        print("\n" + "="*60)
        print("TASK 1: EXTRACT_FROM_API")
        print("="*60)
        
        # Simulasi API response
        extracted_data = [
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
            },
            {
                "symbol": "ADAUSDT",
                "price": 0.98,
                "quantity": 1000.0,
                "event_time": 1700000003000,
                "exchange": "BINANCE"
            },
        ]
        
        print(f"✅ Extracted {len(extracted_data)} records from Binance API")
        print(f"   Sample: {extracted_data[0]}")
        
        # Dalam Airflow: simpan ke XCom
        # context['task_instance'].xcom_push(key='raw_data', value=extracted_data)
        
        return extracted_data
    
    @staticmethod
    def task_serialize_to_avro(raw_data: List[Dict], **context):
        """
        Task 2: Serialize JSON ke Avro bytes
        Input: JSON data (dari XCom atau parameter)
        Output: Avro bytes (serialized)
        """
        print("\n" + "="*60)
        print("TASK 2: SERIALIZE_TO_AVRO")
        print("="*60)
        
        json_str = json.dumps(raw_data)
        avro_bytes = AvroSerializer.serialize(raw_data, "crypto_trade")
        size_info = AvroSerializer.get_size_info(avro_bytes, json_str)
        
        print(f"✅ Serialization completed:")
        print(f"   JSON size: {size_info['json_size_bytes']} bytes")
        print(f"   Avro size: {size_info['avro_size_bytes']} bytes")
        print(f"   Compression: {size_info['compression_ratio']:.1f}% smaller")
        print(f"   Records: {len(raw_data)}")
        
        # Dalam Airflow: push ke XCom
        # context['task_instance'].xcom_push(key='avro_data', value=avro_bytes)
        
        return avro_bytes
    
    @staticmethod
    def task_validate_schema(avro_bytes: bytes, **context):
        """
        Task 3: Validate data sesuai schema
        Input: Avro bytes
        Output: Validation result
        """
        print("\n" + "="*60)
        print("TASK 3: VALIDATE_SCHEMA")
        print("="*60)
        
        try:
            # Deserialize untuk validasi
            data = AvroSerializer.deserialize(avro_bytes, "crypto_trade")
            
            # Validation rules
            validations = {
                "record_count_gt_zero": len(data) > 0,
                "all_have_symbol": all("symbol" in r for r in data),
                "all_have_price": all("price" in r for r in data),
                "all_prices_positive": all(r["price"] > 0 for r in data),
                "all_quantities_positive": all(r["quantity"] > 0 for r in data),
            }
            
            all_passed = all(validations.values())
            
            print(f"✅ Data integrity checks:")
            for check_name, result in validations.items():
                status = "✓" if result else "✗"
                print(f"   {status} {check_name}: {result}")
            
            if not all_passed:
                raise ValueError("Schema validation failed!")
            
            print(f"\n✅ All validations PASSED ({len(data)} records)")
            
        except Exception as e:
            print(f"❌ Validation FAILED: {str(e)}")
            raise
        
        return avro_bytes
    
    @staticmethod
    def task_save_to_datalake(avro_bytes: bytes, **context):
        """
        Task 4a: Save Avro bytes ke S3 Data Lake
        Input: Avro bytes
        Output: S3 file path
        """
        print("\n" + "="*60)
        print("TASK 4A: SAVE_TO_DATALAKE (S3)")
        print("="*60)
        
        # Dalam praktik real: gunakan boto3
        # s3_client = boto3.client('s3')
        # bucket = 'my-data-lake'
        # key = f'crypto/raw/{datetime.now().strftime("%Y/%m/%d")}/trades.avro'
        # s3_client.put_object(Bucket=bucket, Key=key, Body=avro_bytes)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        s3_path = f"s3://my-data-lake/crypto/raw/{datetime.now().strftime('%Y/%m/%d')}/trades_{datetime.now().timestamp()}.avro"
        
        print(f"✅ Saved to S3 Data Lake")
        print(f"   Path: {s3_path}")
        print(f"   Size: {len(avro_bytes)} bytes ({len(avro_bytes)/1024/1024:.2f} MB)")
        print(f"   Timestamp: {timestamp}")
        
        return s3_path
    
    @staticmethod
    def task_save_to_postgres(avro_bytes: bytes, **context):
        """
        Task 4b: Insert data ke PostgreSQL (Operational DB)
        Input: Avro bytes
        Output: Row count inserted
        """
        print("\n" + "="*60)
        print("TASK 4B: SAVE_TO_POSTGRES")
        print("="*60)
        
        # Deserialize untuk insert
        data = AvroSerializer.deserialize(avro_bytes, "crypto_trade")
        
        # Dalam praktik real: gunakan psycopg2
        # conn = psycopg2.connect("postgresql://user:pass@localhost/db")
        # cursor = conn.cursor()
        # for row in data:
        #     cursor.execute(
        #         "INSERT INTO crypto_trades (symbol, price, quantity, event_time, exchange) VALUES (%s, %s, %s, %s, %s)",
        #         (row['symbol'], row['price'], row['quantity'], row['event_time'], row['exchange'])
        #     )
        # conn.commit()
        
        print(f"✅ Inserted to PostgreSQL")
        print(f"   Database: postgresql://localhost/dataeng")
        print(f"   Table: crypto_trades")
        print(f"   Rows inserted: {len(data)}")
        
        for row in data:
            print(f"   - {row['symbol']}: ${row['price']}")
        
        return len(data)
    
    @staticmethod
    def task_save_to_bigquery(avro_bytes: bytes, **context):
        """
        Task 4c: Upload ke BigQuery (Analytics)
        Input: Avro bytes
        Output: Job ID
        """
        print("\n" + "="*60)
        print("TASK 4C: SAVE_TO_BIGQUERY")
        print("="*60)
        
        data = AvroSerializer.deserialize(avro_bytes, "crypto_trade")
        
        # Dalam praktik real: gunakan google-cloud-bigquery
        # from google.cloud import bigquery
        # bq_client = bigquery.Client(project="my-project")
        # table_id = "my-project.raw.crypto_trades"
        # job = bq_client.insert_rows_json(table_id, data)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        job_id = f"job_{int(datetime.now().timestamp())}"
        
        print(f"✅ Uploaded to BigQuery")
        print(f"   Project: my-gcp-project")
        print(f"   Dataset: raw")
        print(f"   Table: crypto_trades")
        print(f"   Rows: {len(data)}")
        print(f"   Job ID: {job_id}")
        print(f"   Timestamp: {timestamp}")
        
        return job_id
    
    @staticmethod
    def task_aggregate_daily(avro_bytes: bytes, **context):
        """
        Task 5: Aggregate data per hari
        Input: Avro bytes
        Output: Aggregated Avro bytes
        """
        print("\n" + "="*60)
        print("TASK 5: AGGREGATE_DAILY")
        print("="*60)
        
        data = AvroSerializer.deserialize(avro_bytes, "crypto_trade")
        
        # Group by symbol
        aggregates = {}
        for row in data:
            symbol = row["symbol"]
            if symbol not in aggregates:
                aggregates[symbol] = {
                    "symbol": symbol,
                    "prices": [],
                    "quantities": []
                }
            aggregates[symbol]["prices"].append(row["price"])
            aggregates[symbol]["quantities"].append(row["quantity"])
        
        # Create aggregated records
        batch_date = datetime.now().strftime("%Y-%m-%d")
        agg_data = [
            {
                "symbol": agg["symbol"],
                "avg_price": sum(agg["prices"]) / len(agg["prices"]),
                "min_price": min(agg["prices"]),
                "max_price": max(agg["prices"]),
                "total_quantity": sum(agg["quantities"]),
                "record_count": len(agg["prices"]),
                "batch_date": batch_date
            }
            for agg in aggregates.values()
        ]
        
        agg_avro = AvroSerializer.serialize(agg_data, "price_aggregate")
        
        print(f"✅ Daily aggregation completed:")
        print(f"   Input records: {len(data)}")
        print(f"   Aggregated symbols: {len(agg_data)}")
        print(f"   Batch date: {batch_date}")
        
        for agg in agg_data:
            print(f"   - {agg['symbol']}: avg ${agg['avg_price']:.2f}, qty {agg['total_quantity']}")
        
        return agg_avro


# ============================================================================
# PART 4: DAG Orchestration Simulation
# ============================================================================

def simulate_airflow_dag():
    """
    Simulasi DAG di Airflow
    
    Alur:
    extract_api
        ↓
    serialize_avro
        ↓
    validate_schema
        ↓ (branching)
        ├→ save_to_datalake (S3)
        ├→ save_to_postgres
        ├→ save_to_bigquery
        └→ aggregate_daily
    """
    
    print("\n" + "🎯" * 40)
    print("SIMULATING AIRFLOW DAG: crypto_batch_etl")
    print("🎯" * 40)
    
    # Task 1: Extract
    context = {"task_instance": None}  # Simulasi context
    
    raw_data = AirflowTasks.task_extract_from_api(**context)
    
    # Task 2: Serialize
    avro_bytes = AirflowTasks.task_serialize_to_avro(raw_data, **context)
    
    # Task 3: Validate
    validated_avro = AirflowTasks.task_validate_schema(avro_bytes, **context)
    
    # Task 4: Distribute (Parallel execution)
    print("\n" + "="*60)
    print("PARALLEL DISTRIBUTION")
    print("="*60)
    
    s3_path = AirflowTasks.task_save_to_datalake(validated_avro, **context)
    pg_count = AirflowTasks.task_save_to_postgres(validated_avro, **context)
    bq_job = AirflowTasks.task_save_to_bigquery(validated_avro, **context)
    
    # Task 5: Aggregate
    agg_avro = AirflowTasks.task_aggregate_daily(validated_avro, **context)
    
    # Summary
    print("\n" + "="*60)
    print("DAG EXECUTION SUMMARY")
    print("="*60)
    print(f"""
✅ Pipeline completed successfully!

Results:
├── Data Lake (S3): {s3_path}
├── Operational DB (PostgreSQL): {pg_count} rows inserted
├── Analytics (BigQuery): Job {bq_job}
└── Daily Aggregate: {len(AvroSerializer.deserialize(agg_avro, 'price_aggregate'))} symbols

Performance:
├── Data processed: {len(raw_data)} records
├── Serialization: Avro (optimized for batch processing)
├── Distribution: 3 destinations simultaneously
└── Data governance: Schema-validated across all steps
    """)


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print("\n" + "🚀" * 30)
    print("AIRFLOW BATCH ETL WITH AVRO SERIALIZATION")
    print("🚀" * 30)
    
    simulate_airflow_dag()
    
    print("\n" + "="*60)
    print("KEY PATTERNS FOR AIRFLOW BATCH PROCESSING")
    print("="*60)
    print("""
1. **Schema Registry Pattern**
   - Centralized schema management
   - Single source of truth
   - Easy versioning & evolution

2. **Serialize Once, Use Many Pattern**
   - Extract → Serialize to Avro (once)
   - Use same bytes for multiple destinations
   - Cost-efficient (less computation)

3. **XCom Pattern**
   - Task 1: Extract & Serialize → XCom
   - Task 2: Pull, Validate → XCom
   - Task 3: Pull, Distribute → Multiple destinations

4. **Parallel Distribution**
   - Serialize once
   - Send same data to S3, DB, DW simultaneously
   - Reduces latency & improves efficiency

5. **Data Governance**
   - Schema enforced at serialization
   - Validation before distribution
   - Audit trail through DAG execution
    """)
