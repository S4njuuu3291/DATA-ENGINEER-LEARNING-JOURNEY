# Join Optimization — Broadcast vs Shuffle Join

> **Learning Objective:** Master join strategies for optimal performance.

## Join Strategies

### 1. Broadcast Hash Join (Fast)
**When:** One table is small (< 10 MB)

```python
from pyspark.sql.functions import broadcast

big_df.join(broadcast(small_df), "id")
```

**How it works:**
```
1. Copy small table to ALL executors (in memory)
2. Join locally on each executor
3. NO SHUFFLE needed!
```

**Performance:** 10-100x faster than shuffle join

---

### 2. Sort-Merge Join (Default for Large tables)
**When:** Both tables are large

```python
large_df1.join(large_df2, "id")
```

**How it works:**
```
1. Shuffle BOTH tables by join key
2. Sort partitions
3. Merge sorted partitions
```

**Cost:** 2x shuffle (both tables)

---

## Auto-Broadcast Threshold

Spark auto-broadcasts if table < 10 MB:

```python
# Check current setting
spark.conf.get("spark.sql.autoBroadcastJoinThreshold")
# Default: 10485760 (10 MB)

# Increase for larger broadcasts
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "50MB")
```

---

## Join Types

```python
# Inner join (default)
df1.join(df2, "id")

# Left outer
df1.join(df2, "id", "left")

# Right outer
df1.join(df2, "id", "right")

# Full outer
df1.join(df2, "id", "full")

# Cross join (⚠️ DANGEROUS!)
df1.crossJoin(df2)  # Cartesian product!
```

---

## Summary

- **Broadcast join:** Fast, for small tables (< 10 MB)
- **Sort-merge join:** Default for large × large
- **Auto-broadcast:** Configurable threshold
- **Always:** Filter before join to reduce data

---

**Previous:** [← Shuffle Mechanics](02-shuffle-mechanics.md) | **Next:** [Skew Handling](04-skew-handling.md)
