from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import os

def write_to_postgres(batch_df, batch_id,db_url, db_properties):
    try:
        # Add batch metadata
        batch_with_meta = batch_df \
            .withColumn("batch_id", lit(batch_id)) \
            .withColumn("processed_at", current_timestamp())
        
        # Write dengan upsert semantics
        batch_with_meta.write \
            .jdbc(
                url=db_url,
                table="sales_metrics",
                mode="append",  # But table has unique constraint
                properties=db_properties
            )
        
        print(f"Batch {batch_id}: Written {batch_df.count()} rows")
        
    except Exception as e:
        print(f"Batch {batch_id} FAILED: {e}")
        # In production: send alert, write to DLQ
        raise  # Re-raise untuk trigger retry

create_table_query = """
    CREATE TABLE if not exists sales_metrics (
        window_start TIMESTAMP,
        window_end TIMESTAMP,
        category VARCHAR(100),
        total_sales DOUBLE PRECISION,
        total_quantity INTEGER,
        transaction_count BIGINT,
        avg_transaction_value DOUBLE PRECISION,
        max_delay_seen BIGINT,
        batch_id BIGINT,
        processed_at TIMESTAMP,
        PRIMARY KEY (window_start, category)
    );
"""

import time

def monitor_query(query, name):
    """Monitor streaming query health"""
    while query.isActive:
        status = query.status
        progress = query.lastProgress
        
        if progress:
            print(f"\n=== {name} Status ===")
            print(f"Batch ID: {progress['batchId']}")
            print(f"Input rows: {progress.get('numInputRows', 0)}")
            print(f"Processed rows: {progress.get('processedRowsPerSecond', 0):.2f}/sec")
            print(f"Batch duration: {progress.get('batchDuration', 0)} ms")
            
            # Check for issues
            if progress.get('batchDuration', 0) > 30000:  # > 30 seconds
                print("⚠️  WARNING: Slow batch detected!")
            
            # State metrics
            if 'stateOperators' in progress:
                for state_op in progress['stateOperators']:
                    memory_mb = state_op.get('memoryUsedBytes', 0) / 1024 / 1024
                    print(f"State memory: {memory_mb:.2f} MB")
                    print(f"State rows: {state_op.get('numRowsTotal', 0)}")
        
        time.sleep(10)  # Check every 10 seconds

def graceful_shutdown(queries,spark):
    """Stop queries safely"""
    print("\n🛑 Initiating graceful shutdown...")
    
    for query in queries:
        try:
            # Stop query (finish current batch)
            query.stop()
            print(f"✓ Stopped: {query.name}")
        except Exception as e:
            print(f"✗ Error stopping query: {e}")
    
    # Stop Spark session
    spark.stop()
    print("✓ Spark session stopped")