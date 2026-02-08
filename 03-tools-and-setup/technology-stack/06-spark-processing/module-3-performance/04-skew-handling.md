# Data Skew — Unbalanced Partitions

> **Learning Objective:** Detect and handle skewed data distributions.

## What is Data Skew?

**Skew = uneven data distribution**

Example:
```
Partition 1: 90% of data (slow!)
Partition 2: 5% of data (done quickly)
Partition 3: 5% of data (done quickly, then idle)
```

**Result:** One partition becomes bottleneck!

---

## Detecting Skew

### Check Spark UI
- Tasks tab → look for variance in task duration
- One task takes 10x longer → likely skew

### Programmatically
```python
# Check partition sizes
df.groupBy(spark_partition_id()).count().show()
```

---

## Common Causes

1. **Popular keys** (80-20 distribution)
   ```
   Country data: Indonesia = 90%, others = 10%
   ```

2. **Null values clustered**
   ```
   NULL values all go to one partition
   ```

3. **Poor partitioning key choice**

---

## Solutions

### 1. Salting
Add random prefix to skewed keys:

```python
from pyspark.sql.functions import rand, concat, lit

# Add salt
df_salted = df.withColumn("salted_key", 
    concat(col("key"), lit("_"), (rand() * 10).cast("int")))

# Join on salted key
result = df_salted.join(other_df, "salted_key")
```

### 2. Split Skewed Keys
```python
# Separate skewed from normal
df_skewed = df.filter(df.key == "popular_value")
df_normal = df.filter(df.key != "popular_value")

# Process separately
result = df_normal.join(...).union(df_skewed.join(...))
```

### 3. Increase Partitions
```python
df.repartition(1000, "key")  # More partitions = smaller chunks
```

---

## Summary

- **Skew:** Uneven partition sizes
- **Impact:** One slow partition = slow job
- **Detection:** Spark UI task variance
- **Solutions:** Salting, split processing, more partitions

---

**Previous:** [← Join Optimization](03-join-optimization.md) | **Next:** [Caching Strategies](05-caching-strategies.md)
