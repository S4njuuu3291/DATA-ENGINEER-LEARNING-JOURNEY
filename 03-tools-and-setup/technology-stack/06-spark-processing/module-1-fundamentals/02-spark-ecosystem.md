# Spark Ecosystem — Unified Analytics Engine

> **Learning Objective:** Understand Spark's comprehensive ecosystem and how it provides a unified platform for batch processing, SQL, streaming, machine learning, and graph processing.

---

## Spark: More Than Just a "Compute Engine"

**Spark is a UNIFIED ANALYTICS ENGINE** — one platform for multiple workloads:

```
┌─────────────────────────────────────────────────┐
│         APACHE SPARK ECOSYSTEM                   │
├─────────────────────────────────────────────────┤
│                                                  │
│  📊 Spark SQL        📡 Spark Streaming         │
│  (SQL queries,       (Real-time processing,     │
│   DataFrames)        Kafka, streaming data)     │
│                                                  │
│  🤖 MLlib            🕸️  GraphX                  │
│  (Machine Learning,  (Graph processing,         │
│   classification,    PageRank, network)         │
│   clustering)                                    │
│                                                  │
└─────────────────────────────────────────────────┘
                       ↓
         ┌─────────────────────────┐
         │   SPARK CORE ENGINE     │
         │   (RDD, scheduling,     │
         │    memory management)   │
         └─────────────────────────┘
```

---

## 1. Spark SQL — Query and DataFrame Processing

**Purpose:** Query structured data using SQL or DataFrame API

```python
# SQL approach
spark.sql("""
    SELECT country, COUNT(*) as total
    FROM users
    WHERE age > 30
    GROUP BY country
""").show()

# DataFrame API (equivalent)
df.filter(df.age > 30).groupBy("country").count().show()
```

**Use Cases:**
- ETL pipelines (extract, transform, load)
- Data warehousing queries
- Business intelligence reporting
- Structured data processing

---

## 2. Spark Streaming — Real-Time Data Processing

**Purpose:** Process streaming data in real-time

```python
# Read from Kafka
df_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .load()

# Process with micro-batches
df_stream.groupBy("user_id").count() \
    .writeStream \
    .format("console") \
    .start()
```

**Use Cases:**
- Real-time analytics dashboards
- Fraud detection (immediate alerting)
- IoT sensor processing (millions events/sec)
- Live monitoring systems

---

## 3. MLlib — Distributed Machine Learning

**Purpose:** Train and deploy ML models on big data

```python
from pyspark.ml.classification import LogisticRegression

# Train on terabytes of data
lr = LogisticRegression(featuresCol="features", labelCol="label")
model = lr.fit(training_df)  # Distributed training!

# Predict at scale
predictions = model.transform(test_df)
```

**Use Cases:**
- Classification (spam detection, churn prediction)
- Clustering (customer segmentation)
- Recommendation systems (collaborative filtering)
- Predictive analytics at scale

---

## 4. GraphX — Graph and Network Processing

**Purpose:** Analyze graph-structured data

```python
from pyspark import GraphFrame

# Social network analysis
result = graph.pageRank(resetProbability=0.15, maxIter=10)
```

**Use Cases:**
- Social network analysis (influencer detection)
- Fraud detection (pattern recognition)
- Network topology optimization
- Relationship mining

---

## Why "Unified" Matters?

### Traditional Approach (Pre-Spark):
```
Batch processing  → Hadoop MapReduce
SQL queries       → Hive (on Hadoop)
Streaming         → Storm or Flink
Machine learning  → Mahout or custom

Problems:
❌ Different tools = different codebases
❌ Different team skillsets required
❌ Data movement between systems (inefficient!)
❌ Integration complexity
```

### Spark Approach:
```
Batch, SQL, Streaming, ML → ALL in Spark

Benefits:
✅ Single codebase (Python/Scala/Java)
✅ One cluster, one skillset
✅ Data stays in memory (no movement)
✅ Easy integration between components
```

---

## Real-World Unified Pipeline Example

```python
# 1. Batch ETL (Spark SQL)
df_raw = spark.read.parquet("transactions/")
df_clean = df_raw.filter(...).transform(...)

# 2. Feature engineering (MLlib)
from pyspark.ml.feature import VectorAssembler
df_features = VectorAssembler(...).transform(df_clean)

# 3. Train model (MLlib)
model = LogisticRegression().fit(df_features)

# 4. Real-time prediction (Streaming + MLlib)
stream = spark.readStream.format("kafka").load()
predictions = model.transform(stream)

# ALL in one platform!
```

**Advantages:**
- No data export/import between systems
- Shared cluster resources
- Consistent APIs across components
- Easier maintenance and deployment

---

## Summary

**Spark Components:**
- **Spark SQL:** Structured data processing
- **Spark Streaming:** Real-time analytics
- **MLlib:** Distributed machine learning
- **GraphX:** Graph processing

**Unified Platform:** Single codebase, cluster, and skillset for all data workloads.

---

**Previous:** [← Why Spark Exists](01-why-spark-exists.md) | **Next:** [In-Memory Processing →](03-in-memory-processing.md)
