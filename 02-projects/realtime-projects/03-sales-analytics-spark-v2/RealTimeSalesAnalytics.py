from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import os
from utils import * # Pastikan write_to_postgres ada di sini
from sqlalchemy import create_engine, text

# 1. Inisialisasi Spark dengan Package yang Lengkap
spark = SparkSession.builder \
    .appName("RealTimeSalesAnalytics") \
    .master("local[*]") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.postgresql:postgresql:42.7.2") \
    .config("spark.sql.shuffle.partitions", "4") \
    .getOrCreate()

spark.sparkContext.setLogLevel("OFF") # Ganti dari "ERROR" ke "OFF" kalau mau beneran sunyi

# 2. Skema Data
transaction_schema = StructType([
    StructField("transaction_id", StringType(), False),
    StructField("category", StringType(), False),
    StructField("amount", DoubleType(), False),
    StructField("quantity", IntegerType(), False),
    StructField("event_timestamp", StringType(), False),
    StructField("customer_id", StringType(), False)
])

# 3. Baca Stream Kafka
raw_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "sales_events") \
    .option("startingOffsets", "earliest") \
    .option("maxOffsetsPerTrigger", "200") \
    .load()

# 4. Transformasi & Agregasi
parsed_stream = raw_stream.select(
    from_json(col("value").cast("string"), transaction_schema).alias("transaction"),
    col("timestamp").alias("kafka_timestamp")
).select("transaction.*", "kafka_timestamp")

final_stream = parsed_stream \
    .withColumn("event_time", to_timestamp(col("event_timestamp"), "yyyy-MM-dd'T'HH:mm:ss.SSSSSS")) \
    .withColumn("processing_delay_seconds", unix_timestamp(col("kafka_timestamp")) - unix_timestamp(col("event_time"))) \
    .filter(col("amount") > 0) \
    .withWatermark("event_time", "10 minutes")

output_stream = final_stream \
    .groupBy(window(col("event_time"), "5 minutes"), col("category")) \
    .agg(
        sum("amount").alias("total_sales"),
        sum("quantity").alias("total_quantity"),
        count("transaction_id").alias("transaction_count"),
        round(avg("amount"), 2).alias("avg_transaction_value"),
        max("processing_delay_seconds").alias("max_delay_seen")
    ).select(
        col("window.start").alias("window_start"),
        col("window.end").alias("window_end"),
        "category", "total_sales", "total_quantity", "transaction_count", "avg_transaction_value", "max_delay_seen"
    )

# 5. Konfigurasi Database & Upsert Logic
db_url = "jdbc:postgresql://localhost:5432/sales_stream_spark"
db_properties = {
    "user": "sales_admin",
    "password": "sales_pass",
    "driver": "org.postgresql.Driver"
}

engine = create_engine(f"postgresql+psycopg2://{db_properties['user']}:{db_properties['password']}@localhost:5432/sales_stream_spark")

# Fungsi menulis ke Postgres dengan logika UPSERT (PENTING!)
def write_to_postgres_upsert(batch_df, batch_id):
    # 1. Simpan data batch ke tabel temporary
    batch_df.write \
        .jdbc(url=db_url, table="temp_sales_metrics", mode="overwrite", properties=db_properties)
    
    # 2. Query Upsert dengan kolom yang disebutkan satu per satu (Explicit)
    # Sesuaikan urutan kolom ini dengan struktur tabel sales_metrics kamu
    upsert_query = f"""
        INSERT INTO sales_metrics (
            window_start, window_end, category, total_sales, 
            total_quantity, transaction_count, avg_transaction_value, 
            max_delay_seen, batch_id, processed_at
        )
        SELECT 
            window_start, window_end, category, total_sales, 
            total_quantity, transaction_count, avg_transaction_value, 
            max_delay_seen, {batch_id} as batch_id, CURRENT_TIMESTAMP as processed_at 
        FROM temp_sales_metrics
        ON CONFLICT (window_start, category) 
        DO UPDATE SET 
            total_sales = EXCLUDED.total_sales,
            total_quantity = EXCLUDED.total_quantity,
            transaction_count = EXCLUDED.transaction_count,
            avg_transaction_value = EXCLUDED.avg_transaction_value,
            max_delay_seen = EXCLUDED.max_delay_seen,
            batch_id = EXCLUDED.batch_id,
            processed_at = EXCLUDED.processed_at;
    """
    
    # Eksekusi pakai engine SQLAlchemy
    with engine.connect() as conn:
        conn.execute(text(upsert_query))
        conn.commit()
    print(f"Batch {batch_id}: Database Updated via Upsert.")

# 6. Jalankan Sink (Database)
# Gunakan checkpoint tunggal di sini agar progres tersimpan
db_query = output_stream \
    .writeStream \
    .foreachBatch(write_to_postgres_upsert) \
    .outputMode("update") \
    .trigger(processingTime="10 seconds") \
    .option("checkpointLocation", "./checkpoint/sales_analytics") \
    .start()

# 7. Jalankan Sink (Console) untuk monitoring
console_query = output_stream \
    .writeStream \
    .outputMode("update") \
    .format("console") \
    .option("truncate", "false") \
    .trigger(processingTime="10 seconds") \
    .start()

try:
    # Program akan jalan terus sampai kamu pencet Ctrl+C
    db_query.awaitTermination()
except KeyboardInterrupt:
    print("Mematikan sistem...")
    db_query.stop()
    console_query.stop()
    spark.stop()
