# RDD Fundamentals -Resilient Distributed Dataset

> **Learning Objective:** Understand RDD as Spark's foundational abstraction and when to use it vs DataFrame.

---

## What is RDD?

**RDD = Resilient Distributed Dataset**

The original low-level API in Spark with three key properties:

### 1. **Resilient** (Fault-Tolerant)
- Auto-recovery from failures
- Maintains lineage graph for rebuilding lost partitions

### 2. **Distributed**
- Data split across cluster partitions
- Parallel processing on multiple nodes

### 3. **Dataset**
- Collection of immutable objects
- Type-safe (in Scala/Java)

---

## Three Core Characteristics

### Immutable

```python
rdd1 = sc.parallelize([1, 2, 3, 4, 5])
rdd2 = rdd1.map(lambda x: x * 2)

print(rdd1.collect())  # [1, 2, 3, 4, 5] ← unchanged!
print(rdd2.collect())  # [2, 4, 6, 8, 10] ← new RDD
```

**Why immutable?**
- Thread-safe for parallel processing
- Enables fault tolerance via lineage
- No side effects

### Distributed Across Partitions

```python
rdd = sc.parallelize([1,2,3,4,5,6], numSlices=3)

# Physical distribution:
# Partition 0 → [1, 2]
# Partition 1 → [3, 4]
# Partition 2 → [5, 6]
```

### Fault-Tolerant via Lineage

```python
rdd1 = sc.textFile("data.txt")
rdd2 = rdd1.filter(lambda x: len(x) > 10)
rdd3 = rdd2.map(lambda x: x.upper())

# Lineage: rdd1 → rdd2 → rdd3
# If partition lost → Spark rebuilds from lineage
```

---

## RDD Operations

### Transformations (Lazy)
```python
rdd.map(lambda x: x * 2)
rdd.filter(lambda x: x > 5)
rdd.flatMap(lambda x: x.split())
rdd.distinct()
```

### Actions (Eager)
```python
rdd.collect()      # Return all elements
rdd.count()        # Count elements
rdd.first()        # First element
rdd.take(n)        # First n elements
rdd.saveAsTextFile("output/")
```

---

## RDD vs DataFrame

| Aspect | RDD | DataFrame |
|--------|-----|-----------|
| **Level** | Low-level | High-level |
| **Structure** | Unstructured | Structured (schema) |
| **Optimization** | Manual | Automatic (Catalyst) |
| **Performance** | Slower | Faster (2-10x) |
| **Use Case** | Custom logic, unstructured data | SQL-like ops, structured data |

---

## When to Use RDD?

**✅ Use RDD when:**
- Processing unstructured data (text files, logs)
- Need fine-grained control
- Custom partitioning logic
- Legacy code compatibility

**❌ Use DataFrame when:**
- Structured/semi-structured data (CSV, JSON, Parquet)
- SQL-like operations
- Better performance needed
- Type safety with schema

---

## Summary

- **RDD:** Low-level distributed collection
- **Properties:** Immutable, Distributed, Fault-tolerant 
- **Operations:** Transformations (lazy) + Actions (eager)
- **Modern practice:** Use DataFrame by default, RDD for edge cases

---

**Next:** [DataFrame Basics →](02-dataframe-basics.md)
