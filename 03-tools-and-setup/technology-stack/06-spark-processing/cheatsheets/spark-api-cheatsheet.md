# Spark API Cheatsheet

Quick reference for common Spark operations.

## DataFrame Creation

```python
# From file
df = spark.read.csv("data.csv", header=True, inferSchema=True)
df = spark.read.json("data.json")
df = spark.read.parquet("data.parquet")

# Programmatically
df = spark.createDataFrame(data, ["col1", "col2"])

# With explicit schema
from pyspark.sql.types import *
schema = StructType([
    StructField("name", StringType(), True),
    StructField("age", IntegerType(), True)
])
df = spark.read.schema(schema).json("data.json")
```

## Common Transformations (Lazy)

```python
df.select("col1", "col2")
df.filter(df.age > 30)
df.where(df.age > 30)  # alias for filter
df.groupBy("country").count()
df.orderBy("age", ascending=False)
df.limit(10)
df.withColumn("new_col", ...)
df.drop("col1")
df.distinct()
df.dropDuplicates(["col1"])
```

## Common Actions (Eager)

```python
df.show()
df.show(5, truncate=False)
df.count()
df.collect()  # ⚠️ Dangerous for large data!
df.first()
df.take(10)
df.head(10)
df.describe().show()
df.printSchema()
```

## Joins

```python
# Inner join (default)
df1.join(df2, "id")
df1.join(df2, df1.id == df2.id)

# Other join types
df1.join(df2, "id", "left")
df1.join(df2, "id", "right")
df1.join(df2, "id", "outer")

# Broadcast join
from pyspark.sql.functions import broadcast
big_df.join(broadcast(small_df), "id")
```

## Aggregations

```python
from pyspark.sql.functions import *

df.groupBy("country").agg(
    sum("amount").alias("total"),
    avg("age").alias("avg_age"),
    count("*").alias("count"),
    max("score").alias("max_score")
)
```

## Partitioning

```python
# Check partitions
df.rdd.getNumPartitions()

# Repartition (full shuffle)
df.repartition(100)
df.repartition(100, "key")  # By column

# Coalesce (merge only, no full shuffle)
df.coalesce(10)
```

## Caching

```python
df.cache()
df.persist(StorageLevel.MEMORY_AND_DISK)
df.unpersist()
```

## Debugging

```python
# Explain execution plan
df.explain()
df.explain(True)  # All optimization phases

# Sample data
df.sample(0.1).show()  # 10% sample
```

---

**More:** [Performance Tuning Cheatsheet →](performance-tuning.md)
