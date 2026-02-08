# Partitioning Basics — Foundation of Parallelism

> **Learning Objective:** Understand partitions as the unit of parallelism in Spark.

## What is a Partition?

**Partition = chunk of distributed data**

Think: Pizza slices for multiple people!

```
Whole pizza (data)
↓
8 slices (8 partitions)
↓
8 people eat in parallel (8 executors)
```

---

## Why Partitions Matter

**Formula:**
```
Total Time = Processing Time of LARGEST Partition
```

Not the average — the **slowest** partition determines total time!

---

## Partition Size Guidelines

**Ideal size:** 100-200 MB per partition```

**Too small** (< 10 MB):
- ❌ Too many tasks
- ❌ Coordination overhead

**Too large** (> 1 GB):
- ❌ Memory pressure
- ❌ Slow tasks
- ❌ OOM errors

---

## Checking Partitions

```python
# How many partitions?
df.rdd.getNumPartitions()  # e.g., 200

# Estimate partition size
data_size = 100 GB
num_partitions = 200
partition_size = data_size / num_partitions  # 500 MB each
```

---

## Narrow vs Wide Transformations

### Narrow (Fast)
No data movement between partitions:
```python
df.filter(...)   # Each partition filtered independently
df.map(...)      # Each partition mapped independently
df.select(...)   # Each partition projected independently
```

### Wide (Slow)
Requires shuffle (data movement):
```python
df.groupBy(...)  # Must redistribute by key
df.join(...)     # Must co-locate matching keys
df.distinct()    # Must check all partitions
df.orderBy(...)  # Global sort needs shuffle
```

---

## Summary

- **Partition:** Unit of parallelism (1 partition = 1 task)
- **Size matters:** 100-200 MB ideal
- **Narrow:** No shuffle, fast
- **Wide:** Shuffle required, slow

---

**Next:** [Shuffle Mechanics →](02-shuffle-mechanics.md)
