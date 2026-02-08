# Shuffle Mechanics — Why Spark Slows Down

> **Learning Objective:** Understand shuffle operations and their performance impact.

## What is Shuffle?

**Shuffle = redistributing data across partitions**

Happens when output partition depends on multiple input partitions.

---

## Shuffle Phases

### Phase 1: Map (Write)
```
Each executor:
1. Hash each key → determine target partition
2. Write to local disk by target partition
```

### Phase 2: Network Transfer
```
All partition data for same key
→ moved to same executor
→ via network
```

### Phase 3: Reduce (Read)
```
Each executor:
1. Receive data from all sources
2. Aggregate/process
```

---

## Why Shuffle is Expensive

**4 cost factors:**

1. **Disk I/O** — write intermediate results
2. **Network** — transfer data between nodes
3. **Serialization** — convert objects to bytes
4. **Sorting** — for some operations (sort-merge join)

**Result:** 10-100x slower than narrow operations!

---

## Operations That Trigger Shuffle

```python
df.groupBy("key").agg(...)    # Shuffle!
df.join(other_df, "key")      # Shuffle!
df.distinct()                 # Shuffle!
df.orderBy("column")          # Shuffle!
df.repartition(n)             # Shuffle!
```

---

## Minimizing Shuffles

### 1. Filter Early
```python
# ❌ Bad: shuffle then filter
df.groupBy("country").count().filter(...)

# ✅ Good: filter then shuffle
df.filter(...).groupBy("country").count()
```

### 2. Broadcast Small Tables
```python
# ❌ Bad: shuffle both sides
big_df.join(small_df, "id")

# ✅ Good: broadcast small table
from pyspark.sql.functions import broadcast
big_df.join(broadcast(small_df), "id")
```

### 3. Coalesce vs Repartition
```python
# ❌ Full shuffle
df.repartition(10)

# ✅ Cheap merge (decrease only)
df.coalesce(10)
```

---

## Summary

- **Shuffle:** Data redistribution across cluster
- **Expensive:** Disk + Network + Serialization
- **Triggers:** groupBy, join, distinct, orderBy, repartition
- **Minimize:** Filter early, broadcast small tables, use coalesce

---

**Previous:** [← Partitioning Basics](01-partitioning-basics.md) | **Next:** [Join Optimization →](03-join-optimization.md)
