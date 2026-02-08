import os
# Set JAVA_HOME sebelum import PySpark
os.environ['JAVA_HOME'] = '/usr/lib/jvm/java-17-openjdk-amd64'

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import yaml
from utils import write_to_postgres_price, write_to_postgres_window

# Load Config
config = yaml.safe_load(open(".//config//settings.yml", "r"))
topic = config["kafka"]["topic"]
schema_registry_url = config["schema_registry"]["url"]

packages = [
    "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0",
    "org.postgresql:postgresql:42.7.2",
    "org.apache.spark:spark-avro_2.12:3.5.0",
    "za.co.absa:abris_2.12:6.1.1",
    "io.confluent:kafka-avro-serializer:6.2.1",
    "io.confluent:kafka-schema-registry-client:6.2.1"
]

spark = SparkSession.builder \
    .appName("RealTimeCryptoAnalytics") \
    .master("local[*]") \
    .config("spark.jars.packages", ",".join(packages)) \
    .config("spark.jars.repositories", "https://packages.confluent.io/maven/") \
    .config("spark.sql.shuffle.partitions", "4") \
    .config("spark.sql.session.timeZone", "UTC") \
    .config("spark.driver.memory", "2g") \
    .config("spark.executor.memory", "2g") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

jvm = spark.sparkContext._gateway.jvm

abris_config = jvm.za.co.absa.abris.config.AbrisConfig \
    .fromConfluentAvro() \
    .downloadReaderSchemaByLatestVersion() \
    .andTopicNameStrategy(topic, False) \
    .usingSchemaRegistry(schema_registry_url)

# 3. Read Stream dari Kafka
raw_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", topic) \
    .option("startingOffsets", "earliest") \
    .load()

# 4. Parse Avro menggunakan Native Scala Function
# Kita panggil za.co.absa.abris.avro.functions.from_avro secara native
from_avro_func = jvm.za.co.absa.abris.avro.functions.from_avro

# Penting: Kita bungkus pemanggilan JVM ke dalam Column PySpark
parsed_stream = raw_stream.select(
    Column(from_avro_func(col("value")._jc, abris_config)).alias("data")
).select("data.*")

# 5. Transformasi Waktu
final_stream = parsed_stream \
    .withColumn("event_time", timestamp_seconds(col("event_time"))) \
    .withColumn("processed_time", timestamp_seconds(col("processed_time"))) \
    .withWatermark("event_time", "10 seconds")

# 6. Sinks (Postgres)
query_price = final_stream.writeStream \
    .foreachBatch(write_to_postgres_price) \
    .trigger(processingTime="2 seconds") \
    .outputMode("append") \
    .option("checkpointLocation", ".//checkpoint//crypto_prices") \
    .start()

# 7. OHLC Calculation
ohlc_stream = final_stream \
    .groupBy(window(col("event_time"), "1 minute"), col("symbol")) \
    .agg(
        first("price").alias("open"),
        max("price").alias("high"),
        min("price").alias("low"),
        last("price").alias("close")
    ).select(
        col("window.start").alias("window_start"),
        col("window.end").alias("window_end"),
        "symbol", "open", "high", "low", "close"
    )

query_window_1m = ohlc_stream.writeStream \
    .foreachBatch(write_to_postgres_window) \
    .outputMode("update") \
    .trigger(processingTime="10 seconds") \
    .option("checkpointLocation", ".//checkpoint//window_1m") \
    .start()

if __name__ == "__main__":
    try:
        print(f"🚀 Spark Engine Active. Processing 31-byte Avro records...")
        spark.streams.awaitAnyTermination()
    except KeyboardInterrupt:
        print("🛑 Shutting down...")
        spark.streams.stop()